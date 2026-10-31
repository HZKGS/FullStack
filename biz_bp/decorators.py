"""JWT and role-based access-control decorators."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

import jwt
from bson import ObjectId
from flask import g, jsonify, request

from globals import (
    JWT_ALGORITHM,
    JWT_SECRET,
    blacklist_collection,
    users_collection,
)


def _error(message: str, status: int):
    return jsonify({"error": message}), status


def jwt_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Validate a Bearer JWT, reject logout-blacklisted tokens, and load the user."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return _error("Authorization header must use Bearer <token>", 401)

        token = auth_header[7:].strip()
        if not token:
            return _error("Bearer token is missing", 401)

        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            return _error("Token has expired", 401)
        except jwt.InvalidTokenError:
            return _error("Token is invalid", 401)

        if not payload.get("sub") or not payload.get("jti") or not payload.get("exp"):
            return _error("Token is missing required claims", 401)

        if blacklist_collection.find_one({"jti": payload["jti"]}):
            return _error("Token has been revoked", 401)

        if not ObjectId.is_valid(payload["sub"]):
            return _error("Token subject is invalid", 401)

        user = users_collection.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            return _error("Token user no longer exists", 401)

        g.current_user = user
        g.jwt_payload = payload
        g.jwt_token = token
        return view(*args, **kwargs)

    return wrapper


def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Require the authenticated user loaded by jwt_required to be an admin."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        user = getattr(g, "current_user", None)
        if not user or not user.get("admin", False):
            return _error("Administrator permission required", 403)
        return view(*args, **kwargs)

    return wrapper