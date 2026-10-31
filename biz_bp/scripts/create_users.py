"""Create deterministic demo users with bcrypt password hashes.

Passwords are read only from environment variables and are never printed or
written into source control.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import bcrypt
from bson import ObjectId

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from globals import ensure_indexes, users_collection  # noqa: E402

FIXTURES = [
    ("a00000000000000000000001", "admin", "admin@locallens.local", True, "ADMIN_PASSWORD"),
    ("a00000000000000000000002", "alice", "alice@locallens.local", False, "USER_PASSWORD"),
    ("a00000000000000000000003", "bob", "bob@locallens.local", False, "USER_PASSWORD"),
    ("a00000000000000000000004", "carol", "carol@locallens.local", False, "USER_PASSWORD"),
]


def main() -> None:
    admin_password = os.getenv("ADMIN_PASSWORD")
    user_password = os.getenv("USER_PASSWORD")
    if not admin_password or not user_password:
        raise SystemExit(
            "Set ADMIN_PASSWORD and USER_PASSWORD environment variables before running."
        )
    if len(admin_password) < 8 or len(user_password) < 8:
        raise SystemExit("Demo passwords must contain at least 8 characters.")

    now = datetime.now(timezone.utc)
    for raw_id, username, email, is_admin, password_env in FIXTURES:
        password = admin_password if is_admin else user_password
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        users_collection.update_one(
            {"_id": ObjectId(raw_id)},
            {
                "$set": {
                    "username": username,
                    "email": email,
                    "password_hash": password_hash,
                    "admin": is_admin,
                    "seed_user": True,
                    "created_at": now,
                }
            },
            upsert=True,
        )
        print(f"Upserted user: {username} (admin={is_admin})")

    ensure_indexes()
    print("Demo users ready.")


if __name__ == "__main__":
    main()