"""Small shared validation and JSON serialisation helpers."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from bson import ObjectId
from flask import request


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def json_safe(value: Any) -> Any:
    """Convert BSON/Python values into JSON-compatible values."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def parse_object_id(value: str, field_name: str = "id") -> ObjectId:
    """Parse a MongoDB ObjectId or raise ValueError."""
    if not ObjectId.is_valid(value):
        raise ValueError(f"{field_name} must be a 24-character MongoDB ObjectId")
    return ObjectId(value)


def parse_pagination() -> tuple[int, int, int]:
    """Read pn/ps query parameters and return page, size and skip."""
    try:
        page = int(request.args.get("pn", "1"))
        page_size = int(request.args.get("ps", "20"))
    except ValueError as exc:
        raise ValueError("pn and ps must be integers") from exc

    if page < 1:
        raise ValueError("pn must be greater than or equal to 1")
    if page_size < 1 or page_size > 100:
        raise ValueError("ps must be between 1 and 100")
    return page, page_size, (page - 1) * page_size


def pagination_payload(page: int, page_size: int, total: int) -> dict[str, Any]:
    """Build a consistent pagination metadata object."""
    pages = (total + page_size - 1) // page_size if total else 0
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }