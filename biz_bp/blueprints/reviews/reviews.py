"""Review CRUD endpoints nested under a business resource."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, g, jsonify, request
from pymongo import ASCENDING, DESCENDING

from decorators import admin_required, jwt_required
from globals import businesses_collection, reviews_collection
from utils import (
    json_safe,
    pagination_payload,
    parse_object_id,
    parse_pagination,
    utcnow,
)

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/v1.0/businesses")

SORT_FIELDS = {"created_at", "updated_at", "rating"}


def _validate_review_payload(
    payload: dict[str, Any], *, partial: bool = False
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    clean: dict[str, Any] = {}
    unknown = sorted(set(payload) - {"rating", "text"})
    if unknown:
        errors.append(f"Unsupported fields: {', '.join(unknown)}")

    if not partial:
        missing = sorted(field for field in ("rating", "text") if field not in payload)
        if missing:
            errors.append(f"Missing required fields: {', '.join(missing)}")

    if "rating" in payload:
        rating = payload["rating"]
        if (
            not isinstance(rating, int)
            or isinstance(rating, bool)
            or rating < 1
            or rating > 5
        ):
            errors.append("rating must be an integer from 1 to 5")
        else:
            clean["rating"] = rating

    if "text" in payload:
        text = payload["text"]
        if not isinstance(text, str) or not text.strip() or len(text.strip()) > 5000:
            errors.append("text must be a non-empty string of at most 5000 characters")
        else:
            clean["text"] = text.strip()

    return clean, errors


def _sort_spec() -> list[tuple[str, int]]:
    requested = request.args.get("sort", "-created_at")
    descending = requested.startswith("-")
    field = requested[1:] if descending else requested
    if field not in SORT_FIELDS:
        raise ValueError(f"sort must be one of: {', '.join(sorted(SORT_FIELDS))}")
    return [(field, DESCENDING if descending else ASCENDING), ("_id", ASCENDING)]


def _recalculate_business_rating(business_id) -> None:
    """Recompute denormalised rating and review_count for a business."""
    summary = list(
        reviews_collection.aggregate(
            [
                {"$match": {"business_id": business_id}},
                {
                    "$group": {
                        "_id": "$business_id",
                        "review_count": {"$sum": 1},
                        "rating": {"$avg": "$rating"},
                    }
                },
            ]
        )
    )
    if summary:
        rating = round(float(summary[0]["rating"]), 2)
        review_count = int(summary[0]["review_count"])
    else:
        rating = 0.0
        review_count = 0
    businesses_collection.update_one(
        {"_id": business_id},
        {"$set": {"rating": rating, "review_count": review_count, "updated_at": utcnow()}},
    )


def _business_or_404(business_id: str):
    business_object_id = parse_object_id(business_id, "business_id")
    business = businesses_collection.find_one({"_id": business_object_id})
    return business_object_id, business


@reviews_bp.get("/<string:business_id>/reviews")
def list_reviews(business_id: str):
    """List reviews for one business with pagination and filters."""
    try:
        business_object_id, business = _business_or_404(business_id)
        page, page_size, skip = parse_pagination()
        sort_spec = _sort_spec()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not business:
        return jsonify({"error": "Business not found"}), 404

    filters: dict[str, Any] = {"business_id": business_object_id}
    rating_raw = request.args.get("rating")
    if rating_raw is not None:
        try:
            rating = int(rating_raw)
        except ValueError:
            return jsonify({"error": "rating must be an integer"}), 400
        if not 1 <= rating <= 5:
            return jsonify({"error": "rating must be between 1 and 5"}), 400
        filters["rating"] = rating

    total = reviews_collection.count_documents(filters)
    documents = (
        reviews_collection.find(filters)
        .sort(sort_spec)
        .skip(skip)
        .limit(page_size)
    )
    return jsonify(
        {
            "business_id": business_id,
            "items": json_safe(list(documents)),
            **pagination_payload(page, page_size, total),
        }
    ), 200


@reviews_bp.post("/<string:business_id>/reviews")
@jwt_required
def create_review(business_id: str):
    """Create one review for a business as an authenticated user."""
    try:
        business_object_id, business = _business_or_404(business_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if not business:
        return jsonify({"error": "Business not found"}), 404

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "JSON object body is required"}), 400
    clean, errors = _validate_review_payload(payload)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    user_id = g.current_user["_id"]
    duplicate = reviews_collection.find_one(
        {"business_id": business_object_id, "user_id": user_id}
    )
    if duplicate:
        return jsonify({"error": "This user already reviewed this business"}), 409

    now = utcnow()
    document = {
        "business_id": business_object_id,
        "user_id": user_id,
        "rating": clean["rating"],
        "text": clean["text"],
        "created_at": now,
        "updated_at": now,
    }
    result = reviews_collection.insert_one(document)
    document["_id"] = result.inserted_id
    _recalculate_business_rating(business_object_id)
    return (
        jsonify(json_safe(document)),
        201,
        {
            "Location": (
                f"/api/v1.0/businesses/{business_id}/reviews/{result.inserted_id}"
            )
        },
    )


@reviews_bp.get("/<string:business_id>/reviews/<string:review_id>")
def get_review(business_id: str, review_id: str):
    """Return one review belonging to the specified business."""
    try:
        business_object_id = parse_object_id(business_id, "business_id")
        review_object_id = parse_object_id(review_id, "review_id")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not businesses_collection.find_one({"_id": business_object_id}):
        return jsonify({"error": "Business not found"}), 404

    review = reviews_collection.find_one(
        {"_id": review_object_id, "business_id": business_object_id}
    )
    if not review:
        return jsonify({"error": "Review not found"}), 404
    return jsonify(json_safe(review)), 200


@reviews_bp.put("/<string:business_id>/reviews/<string:review_id>")
@jwt_required
def update_review(business_id: str, review_id: str):
    """Update an owned review; administrators may update any review."""
    try:
        business_object_id = parse_object_id(business_id, "business_id")
        review_object_id = parse_object_id(review_id, "review_id")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not businesses_collection.find_one({"_id": business_object_id}):
        return jsonify({"error": "Business not found"}), 404

    review = reviews_collection.find_one(
        {"_id": review_object_id, "business_id": business_object_id}
    )
    if not review:
        return jsonify({"error": "Review not found"}), 404

    current_user = g.current_user
    if review.get("user_id") != current_user["_id"] and not current_user.get(
        "admin", False
    ):
        return jsonify({"error": "You may only edit your own review"}), 403

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "JSON object body is required"}), 400
    clean, errors = _validate_review_payload(payload, partial=True)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400
    if not clean:
        return jsonify({"error": "At least one of rating or text is required"}), 400

    clean["updated_at"] = utcnow()
    reviews_collection.update_one({"_id": review_object_id}, {"$set": clean})
    _recalculate_business_rating(business_object_id)
    updated = reviews_collection.find_one({"_id": review_object_id})
    return jsonify(json_safe(updated)), 200


@reviews_bp.delete("/<string:business_id>/reviews/<string:review_id>")
@jwt_required
@admin_required
def delete_review(business_id: str, review_id: str):
    """Delete any review as an administrator."""
    try:
        business_object_id = parse_object_id(business_id, "business_id")
        review_object_id = parse_object_id(review_id, "review_id")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not businesses_collection.find_one({"_id": business_object_id}):
        return jsonify({"error": "Business not found"}), 404

    result = reviews_collection.delete_one(
        {"_id": review_object_id, "business_id": business_object_id}
    )
    if result.deleted_count == 0:
        return jsonify({"error": "Review not found"}), 404

    _recalculate_business_rating(business_object_id)
    return "", 204