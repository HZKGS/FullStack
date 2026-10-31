"""Import generated LocalLens JSON with MongoDB's Extended JSON support."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bson import json_util

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from globals import (  # noqa: E402
    businesses_collection,
    ensure_indexes,
    reviews_collection,
)


def load_documents(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return json_util.loads(handle.read())


def main() -> None:
    parser = argparse.ArgumentParser(description="Import LocalLens seed data")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing businesses/reviews before importing (destructive)",
    )
    args = parser.parse_args()

    business_path = ROOT / "data" / "businesses.json"
    review_path = ROOT / "data" / "reviews.json"
    if not business_path.exists() or not review_path.exists():
        raise SystemExit("Seed JSON is missing; run scripts/make_seed_data.py first")

    if args.reset:
        businesses_collection.delete_many({})
        reviews_collection.delete_many({})

    if businesses_collection.count_documents({}) or reviews_collection.count_documents({}):
        raise SystemExit(
            "Target collections are not empty. Re-run with --reset only if deletion is intended."
        )

    businesses = load_documents(business_path)
    reviews = load_documents(review_path)
    businesses_collection.insert_many(businesses)
    reviews_collection.insert_many(reviews)
    ensure_indexes()
    print(f"Imported {len(businesses)} businesses and {len(reviews)} reviews.")


if __name__ == "__main__":
    main()