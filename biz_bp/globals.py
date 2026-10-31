"""Shared configuration and MongoDB collections for the LocalLens API."""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from pymongo import ASCENDING, DESCENDING, GEOSPHERE, TEXT, MongoClient


def _load_local_env() -> None:
    """Load a gitignored .env.local without adding a dotenv dependency."""
    env_path = Path(__file__).with_name(".env.local")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_local_env()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "locallens")

# A generated development secret is safe to keep in memory, but it changes on
# restart. Production/coursework runs should set JWT_SECRET explicitly.
JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_hex(32)
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY_SECONDS", "28800"))

CLIENT = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
DB = CLIENT[DB_NAME]

users_collection = DB["users"]
businesses_collection = DB["businesses"]
reviews_collection = DB["reviews"]
blacklist_collection = DB["blacklist"]


def ensure_indexes() -> None:
    """Create indexes required by authentication and advanced queries."""
    users_collection.create_index([("username", ASCENDING)], unique=True)
    blacklist_collection.create_index([("jti", ASCENDING)], unique=True)
    blacklist_collection.create_index(
        [("expires_at", ASCENDING)], expireAfterSeconds=0
    )
    businesses_collection.create_index([("location", GEOSPHERE)])
    businesses_collection.create_index(
        [("name", TEXT), ("description", TEXT), ("town", TEXT)]
    )
    businesses_collection.create_index(
        [("town", ASCENDING), ("categories", ASCENDING)]
    )
    reviews_collection.create_index(
        [("business_id", ASCENDING), ("created_at", DESCENDING)]
    )
    reviews_collection.create_index([("user_id", ASCENDING)])