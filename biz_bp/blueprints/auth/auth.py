"""Registration, JWT login and logout endpoints."""

from __future__ import annotations

import re
from datetime import timedelta, timezone
from datetime import datetime
from uuid import uuid4

import bcrypt
import jwt
from bson import ObjectId
from flask import Blueprint, g, jsonify, request
from pymongo.errors import DuplicateKeyError

from decorators import jwt_required
from globals import (
    JWT_ALGORITHM,
    JWT_EXPIRY_SECONDS,
    JWT_SECRET,
    blacklist_collection,
    users_collection,
)
from utils import json_safe, utcnow

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1.0")

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,50}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _serialise_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user.get("email"),
        "admin": bool(user.get("admin", False)),
        "created_at": json_safe(user.get("created_at")),
    }


def _credentials_from_request() -> tuple[object, object]:
    payload = request.get_json(silent=True) or {}
    username = payload.get("username", request.args.get("username"))
    password = payload.get("password", request.args.get("password"))
    return username, password


def _issue_token(user: dict) -> dict:
    issued_at = utcnow()
    expires_at = issued_at + timedelta(seconds=JWT_EXPIRY_SECONDS)
    payload = {
        "sub": str(user["_id"]),
        "username": user["username"],
        "admin": bool(user.get("admin", False)),
        "iat": issued_at,
        "exp": expires_at,
        "jti": uuid4().hex,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {
        "token": token,
        "token_type": "Bearer",
        "expires_in": JWT_EXPIRY_SECONDS,
        "user": _serialise_user(user),
    }


@auth_bp.post("/users")
def register_user():
    """Register a non-admin user."""
    payload = request.get_json(silent=True) or {}
    username = payload.get("username")
    password = payload.get("password")
    email = payload.get("email")

    if not isinstance(username, str) or not USERNAME_PATTERN.fullmatch(username):
        return jsonify(
            {"error": "username must be 3-50 letters, numbers, '_' or '-'"}
        ), 400
    if not isinstance(password, str) or len(password) < 8:
        return jsonify({"error": "password must contain at least 8 characters"}), 400
    if email is not None and (
        not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email)
    ):
        return jsonify({"error": "email is invalid"}), 400

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    document = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "admin": False,
        "created_at": utcnow(),
    }

    try:
        result = users_collection.insert_one(document)
    except DuplicateKeyError:
        return jsonify({"error": "username already exists"}), 409

    document["_id"] = result.inserted_id
    return jsonify({"user": _serialise_user(document)}), 201


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate with username/password and return a JWT.

    POST JSON is the preferred form. GET query parameters are retained because
    the module endpoint specification explicitly lists GET /login.
    """
    username, password = _credentials_from_request()
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "username and password are required"}), 400

    user = users_collection.find_one({"username": username})
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    stored_hash = user.get("password_hash", "")
    if isinstance(stored_hash, bytes):
        stored_hash_bytes = stored_hash
    elif isinstance(stored_hash, str):
        stored_hash_bytes = stored_hash.encode("utf-8")
    else:
        stored_hash_bytes = b""

    try:
        password_matches = bcrypt.checkpw(
            password.encode("utf-8"), stored_hash_bytes
        )
    except ValueError:
        password_matches = False

    if not password_matches:
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify(_issue_token(user)), 200


@auth_bp.get("/logout")
@jwt_required
def logout():
    """Revoke the current JWT by adding its jti to the blacklist."""
    payload = g.jwt_payload
    expires_at = datetime.fromtimestamp(int(payload["exp"]), tz=timezone.utc)
    blacklist_collection.update_one(
        {"jti": payload["jti"]},
        {
            "$setOnInsert": {
                "jti": payload["jti"],
                "user_id": ObjectId(payload["sub"]),
                "expires_at": expires_at,
                "created_at": utcnow(),
            }
        },
        upsert=True,
    )
    return jsonify({"message": "Logged out successfully"}), 200