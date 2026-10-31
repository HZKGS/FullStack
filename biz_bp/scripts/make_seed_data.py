"""Generate deterministic LocalLens seed JSON for MongoDB import.

The generated data is synthetic and intentionally independent of Yelp. It
contains 120 parent businesses and 600 child reviews, with text, numeric,
date, boolean and GeoJSON values.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

SEED = 661
BUSINESS_COUNT = 120
REVIEWS_PER_BUSINESS = 5
BASE_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

TOWNS = [
    ("Belfast", -5.9301, 54.5973, "BT1"),
    ("Derry", -7.3093, 54.9966, "BT48"),
    ("Lisburn", -6.0580, 54.5162, "BT28"),
    ("Newry", -6.3374, 54.1751, "BT34"),
    ("Armagh", -6.6540, 54.3503, "BT61"),
    ("Bangor", -5.6689, 54.6534, "BT20"),
    ("Coleraine", -6.6760, 55.1326, "BT52"),
    ("Enniskillen", -7.6380, 54.3438, "BT74"),
]
CATEGORIES = [
    "Cafe",
    "Restaurant",
    "Bakery",
    "Bookshop",
    "Bar",
    "Deli",
    "Gallery",
    "Grocery",
    "Hotel",
    "Museum",
]
NAME_PREFIXES = [
    "Harbour",
    "Linen",
    "Meadow",
    "Oak",
    "Riverside",
    "North",
    "Bright",
    "Old Town",
    "Copper",
    "Willow",
]
NAME_SUFFIXES = [
    "Kitchen",
    "House",
    "Room",
    "Market",
    "Cafe",
    "Studio",
    "Corner",
    "Larder",
    "Social",
    "Garden",
]
DESCRIPTIONS = [
    "Independent local business with seasonal produce.",
    "Neighbourhood venue focused on accessible service.",
    "Family-run destination with a strong local identity.",
    "Relaxed space for food, drink and community events.",
    "Small team offering carefully selected products.",
]
REVIEW_PHRASES = [
    "Friendly service and a welcoming atmosphere.",
    "Great value and easy to find from the town centre.",
    "The menu was varied and the staff were helpful.",
    "A pleasant visit, although the venue was busy.",
    "Would return and recommend it to friends.",
    "Good quality overall; accessibility information was useful.",
]

# Fixed ObjectIds keep review references valid when create_users.py runs.
USER_IDS = [
    "a00000000000000000000001",
    "a00000000000000000000002",
    "a00000000000000000000003",
    "a00000000000000000000004",
]


def object_id(value: str) -> dict[str, str]:
    return {"$oid": value}


def extended_date(value: datetime) -> dict[str, str]:
    return {"$date": value.isoformat().replace("+00:00", "Z")}


def business_object_id(index: int) -> str:
    return f"{0xB00000000000000000000000 + index:024x}"


def business_name(index: int, category: str) -> str:
    prefix = NAME_PREFIXES[index % len(NAME_PREFIXES)]
    suffix = NAME_SUFFIXES[(index // len(NAME_PREFIXES)) % len(NAME_SUFFIXES)]
    return f"{prefix} {category} {suffix} {index + 1}"


def main() -> None:
    rng = random.Random(SEED)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    businesses: list[dict] = []
    reviews: list[dict] = []

    for business_index in range(BUSINESS_COUNT):
        town, town_lon, town_lat, postcode_prefix = TOWNS[
            business_index % len(TOWNS)
        ]
        categories = rng.sample(CATEGORIES, k=rng.choice([1, 1, 2, 2, 3]))
        longitude = town_lon + rng.uniform(-0.035, 0.035)
        latitude = town_lat + rng.uniform(-0.025, 0.025)
        created_at = BASE_DATE + timedelta(days=business_index * 3)
        business_oid = business_object_id(business_index)

        ratings: list[int] = []
        for review_index in range(REVIEWS_PER_BUSINESS):
            rating = rng.randint(1, 5)
            ratings.append(rating)
            review_date = created_at + timedelta(
                days=10 + review_index * 17,
                hours=rng.randint(8, 20),
            )
            review_number = business_index * REVIEWS_PER_BUSINESS + review_index
            reviews.append(
                {
                    "_id": object_id(f"{0xC00000000000000000000000 + review_number:024x}"),
                    "business_id": object_id(business_oid),
                    "user_id": object_id(USER_IDS[review_index % len(USER_IDS)]),
                    "rating": rating,
                    "text": rng.choice(REVIEW_PHRASES),
                    "created_at": extended_date(review_date),
                    "updated_at": extended_date(review_date),
                }
            )

        average_rating = round(sum(ratings) / len(ratings), 2)
        businesses.append(
            {
                "_id": object_id(business_oid),
                "name": business_name(business_index, categories[0]),
                "town": town,
                "address": f"{rng.randint(1, 180)} Sample Street",
                "postcode": f"{postcode_prefix} {rng.randint(1, 9)}AA",
                "categories": categories,
                "description": rng.choice(DESCRIPTIONS),
                "location": {
                    "type": "Point",
                    "coordinates": [round(longitude, 6), round(latitude, 6)],
                },
                "price_level": rng.randint(1, 4),
                "active": True,
                "rating": average_rating,
                "review_count": len(ratings),
                "created_at": extended_date(created_at),
                "updated_at": extended_date(created_at),
            }
        )

    (DATA_DIR / "businesses.json").write_text(
        json.dumps(businesses, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (DATA_DIR / "reviews.json").write_text(
        json.dumps(reviews, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"Generated {len(businesses)} businesses and {len(reviews)} reviews in {DATA_DIR}"
    )


if __name__ == "__main__":
    main()