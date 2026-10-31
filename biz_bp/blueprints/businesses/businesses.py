"""Business CRUD, aggregation and geospatial query endpoints."""

from __future__ import annotations

import re
from typing import Any

from flask import Blueprint, jsonify, request
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

businesses_bp = Blueprint(
    "businesses", __name__, url_prefix="/api/v1.0/businesses"
)

ALLOWED_BUSINESS_FIELDS = {
    "name",
    "town",
    "address",
    "postcode",
    "categories",
    "description",
    "location",
    "price_level",
    "active",
}
SORT_FIELDS = {"name", "town", "rating", "review_count", "created_at"}


def _validate_business_payload(
    payload: dict[str, Any], *, partial: bool = False
) -> tuple[dict[str, Any], list[str]]:
    """Validate and normalise a business request body."""
    errors: list[str] = []
    clean: dict[str, Any] = {}
    unknown = sorted(set(payload) - ALLOWED_BUSINESS_FIELDS)
    if unknown:
        errors.append(f"Unsupported fields: {', '.join(unknown)}")

    required = {"name", "town", "location"}
    if not partial:
        missing = sorted(field for field in required if field not in payload)
        if missing:
            errors.append(f"Missing required fields: {', '.join(missing)}")

    if "name" in payload:
        name = payload["name"]
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 200:
            errors.append("name must be a non-empty string of at most 200 characters")
        else:
            clean["name"] = name.strip()

    for field in ("town", "address", "postcode"):
        if field in payload:
            value = payload[field]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field} must be a non-empty string")
            else:
                clean[field] = value.strip()

    if "description" in payload:
        description = payload["description"]
        if not isinstance(description, str) or len(description) > 5000:
            errors.append("description must be a string of at most 5000 characters")
        else:
            clean["description"] = description

    if "categories" in payload:
        categories = payload["categories"]
        if (
            not isinstance(categories, list)
            or not categories
            or len(categories) > 10
            or any(
                not isinstance(item, str) or not item.strip() or len(item.strip()) > 80
                for item in categories
            )
        ):
            errors.append("categories must be a list of 1-10 non-empty strings")
        else:
            clean["categories"] = list(
                dict.fromkeys(item.strip() for item in categories)
            )

    if "location" in payload:
        location = payload["location"]
        valid_location = (
            isinstance(location, dict)
            and location.get("type") == "Point"
            and isinstance(location.get("coordinates"), list)
            and len(location["coordinates"]) == 2
            and all(
                isinstance(value, (int, float)) and not isinstance(value, bool)
                for value in location["coordinates"]
            )
        )
        if not valid_location:
            errors.append(
                "location must be GeoJSON {'type':'Point','coordinates':[lon,lat]}"
            )
        else:
            longitude, latitude = location["coordinates"]
            if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
                errors.append("location coordinates are outside valid longitude/latitude")
            else:
                clean["location"] = {
                    "type": "Point",
                    "coordinates": [float(longitude), float(latitude)],
                }

    if "price_level" in payload:
        price_level = payload["price_level"]
        if (
            not isinstance(price_level, int)
            or isinstance(price_level, bool)
            or price_level not in {1, 2, 3, 4}
        ):
            errors.append("price_level must be an integer from 1 to 4")
        else:
            clean["price_level"] = price_level

    if "active" in payload:
        if not isinstance(payload["active"], bool):
            errors.append("active must be a boolean")
        else:
            clean["active"] = payload["active"]

    return clean, errors


def _sort_spec() -> list[tuple[str, int]]:
    requested = request.args.get("sort", "-created_at")
    descending = requested.startswith("-")
    field = requested[1:] if descending else requested
    if field not in SORT_FIELDS:
        raise ValueError(f"sort must be one of: {', '.join(sorted(SORT_FIELDS))}")
    direction = DESCENDING if descending else ASCENDING
    return [(field, direction), ("_id", ASCENDING)]


@businesses_bp.get("")
def list_businesses():
    """List businesses with pagination, text/multi-value filters and sorting."""
    try:
        page, page_size, skip = parse_pagination()
        sort_spec = _sort_spec()
        query = request.args.get("q", "").strip()
        town = request.args.get("town", "").strip()
        categories = [
            value.strip() for value in request.args.getlist("category") if value.strip()
        ]
        min_rating = request.args.get("min_rating")
        max_rating = request.args.get("max_rating")
        active = request.args.get("active")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    filters: dict[str, Any] = {}
    if query:
        escaped = re.escape(query)
        filters["$or"] = [
            {"name": {"$regex": escaped, "$options": "i"}},
            {"description": {"$regex": escaped, "$options": "i"}},
            {"categories": {"$regex": escaped, "$options": "i"}},
        ]
    if town:
        filters["town"] = {"$regex": f"^{re.escape(town)}$", "$options": "i"}
    if categories:
        filters["categories"] = {"$all": categories}

    if min_rating is not None or max_rating is not None:
        rating_filter: dict[str, float] = {}
        try:
            if min_rating is not None:
                rating_filter["$gte"] = float(min_rating)
            if max_rating is not None:
                rating_filter["$lte"] = float(max_rating)
        except ValueError:
            return jsonify({"error": "min_rating and max_rating must be numbers"}), 400
        if any(not 0 <= value <= 5 for value in rating_filter.values()):
            return jsonify({"error": "rating filters must be between 0 and 5"}), 400
        filters["rating"] = rating_filter

    if active is not None:
        if active.lower() not in {"true", "false"}:
            return jsonify({"error": "active must be true or false"}), 400
        filters["active"] = active.lower() == "true"

    total = businesses_collection.count_documents(filters)
    documents = (
        businesses_collection.find(filters)
        .sort(sort_spec)
        .skip(skip)
        .limit(page_size)
    )
    return jsonify(
        {
            "items": json_safe(list(documents)),
            **pagination_payload(page, page_size, total),
        }
    ), 200


@businesses_bp.post("")
@jwt_required
def create_business():
    """Create a business as an authenticated user."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "JSON object body is required"}), 400

    clean, errors = _validate_business_payload(payload)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400

    duplicate = businesses_collection.find_one(
        {
            "name": {"$regex": f"^{re.escape(clean['name'])}$", "$options": "i"},
            "town": {"$regex": f"^{re.escape(clean['town'])}$", "$options": "i"},
        }
    )
    if duplicate:
        return jsonify({"error": "A business with this name and town exists"}), 409

    now = utcnow()
    document = {
        **clean,
        "rating": 0.0,
        "review_count": 0,
        "created_at": now,
        "updated_at": now,
    }
    result = businesses_collection.insert_one(document)
    document["_id"] = result.inserted_id
    return (
        jsonify(json_safe(document)),
        201,
        {"Location": f"/api/v1.0/businesses/{result.inserted_id}"},
    )


@businesses_bp.get("/advanced")
def advanced_business_search():
    """Run the required multi-stage aggregation pipeline."""
    try:
        page, page_size, skip = parse_pagination()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    category = request.args.get("category", "").strip()
    min_rating_raw = request.args.get("min_rating", "0")
    try:
        min_rating = float(min_rating_raw)
    except ValueError:
        return jsonify({"error": "min_rating must be a number"}), 400
    if not 0 <= min_rating <= 5:
        return jsonify({"error": "min_rating must be between 0 and 5"}), 400

    post_unwind_match: dict[str, Any] = {"categories": {"$exists": True}}
    if category:
        post_unwind_match["categories"] = category

    pipeline = [
        {"$match": {"rating": {"$gte": min_rating}, "active": True}},
        {
            "$project": {
                "name": 1,
                "town": 1,
                "address": 1,
                "rating": 1,
                "review_count": 1,
                "categories": 1,
            }
        },
        {"$unwind": "$categories"},
        {"$match": post_unwind_match},
        {"$sort": {"rating": -1, "_id": 1}},
        {"$skip": skip},
        {"$limit": page_size},
    ]
    documents = list(businesses_collection.aggregate(pipeline))
    return jsonify(
        {
            "items": json_safe(documents),
            "page": page,
            "page_size": page_size,
            "pipeline_stages": [
                "$match",
                "$project",
                "$unwind",
                "$match",
                "$sort",
                "$skip",
                "$limit",
            ],
        }
    ), 200


@businesses_bp.get("/stats/by-town")
def business_stats_by_town():
    """Group businesses by town and return counts plus average ratings."""
    limit_raw = request.args.get("limit", "50")
    try:
        limit = int(limit_raw)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400
    if not 1 <= limit <= 200:
        return jsonify({"error": "limit must be between 1 and 200"}), 400

    pipeline = [
        {"$match": {"town": {"$exists": True, "$ne": ""}}},
        {
            "$group": {
                "_id": "$town",
                "business_count": {"$sum": 1},
                "average_rating": {"$avg": "$rating"},
                "review_count": {"$sum": "$review_count"},
            }
        },
        {"$sort": {"business_count": -1, "_id": 1}},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                "town": "$_id",
                "business_count": 1,
                "average_rating": {"$round": ["$average_rating", 2]},
                "review_count": 1,
            }
        },
    ]
    return jsonify({"items": json_safe(list(businesses_collection.aggregate(pipeline)))}), 200


@businesses_bp.get("/nearby")
def nearby_businesses():
    """Find businesses near a longitude/latitude using $geoNear."""
    longitude_raw = request.args.get("longitude")
    latitude_raw = request.args.get("latitude")
    try:
        longitude = float(longitude_raw)
        latitude = float(latitude_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "longitude and latitude are required numbers"}), 400
    if not (-180 <= longitude <= 180 and -90 <= latitude <= 90):
        return jsonify({"error": "coordinates are outside valid ranges"}), 400

    try:
        page, page_size, skip = parse_pagination()
        max_distance = float(request.args.get("max_distance", "5000"))
        min_distance = float(request.args.get("min_distance", "0"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    if max_distance <= 0 or min_distance < 0 or min_distance >= max_distance:
        return jsonify(
            {"error": "distances require 0 <= min_distance < max_distance"}
        ), 400

    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "distanceField": "distance_m",
                "maxDistance": max_distance,
                "minDistance": min_distance,
                "spherical": True,
                "query": {"active": True},
            }
        },
        {"$skip": skip},
        {"$limit": page_size},
        {
            "$project": {
                "name": 1,
                "town": 1,
                "address": 1,
                "categories": 1,
                "rating": 1,
                "review_count": 1,
                "location": 1,
                "distance_m": {"$round": ["$distance_m", 2]},
            }
        },
    ]
    return jsonify(
        {
            "items": json_safe(list(businesses_collection.aggregate(pipeline))),
            "page": page,
            "page_size": page_size,
        }
    ), 200


@businesses_bp.get("/<string:business_id>")
def get_business(business_id: str):
    """Return one business by MongoDB ObjectId."""
    try:
        object_id = parse_object_id(business_id, "business_id")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    document = businesses_collection.find_one({"_id": object_id})
    if not document:
        return jsonify({"error": "Business not found"}), 404
    return jsonify(json_safe(document)), 200


@businesses_bp.put("/<string:business_id>")
@jwt_required
def update_business(business_id: str):
    """Partially update a business as an authenticated user."""
    try:
        object_id = parse_object_id(business_id, "business_id")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "JSON object body is required"}), 400

    clean, errors = _validate_business_payload(payload, partial=True)
    if errors:
        return jsonify({"error": "Validation failed", "details": errors}), 400
    if not clean:
        return jsonify({"error": "At least one supported field is required"}), 400

    clean["updated_at"] = utcnow()
    result = businesses_collection.update_one({"_id": object_id}, {"$set": clean})
    if result.matched_count == 0:
        return jsonify({"error": "Business not found"}), 404

    document = businesses_collection.find_one({"_id": object_id})
    return jsonify(json_safe(document)), 200


@businesses_bp.delete("/<string:business_id>")
@jwt_required
@admin_required
def delete_business(business_id: str):
    """Delete a business and its reviews as an administrator."""
    try:
        object_id = parse_object_id(business_id, "business_id")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    result = businesses_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Business not found"}), 404
    reviews_collection.delete_many({"business_id": object_id})
    return "", 204