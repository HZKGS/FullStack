"""Stateful end-to-end smoke test against the local MongoDB database."""

from __future__ import annotations

import os
import secrets
import sys
import unittest
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("MONGO_URI", "mongodb://127.0.0.1:27017")
os.environ.setdefault("MONGO_DB_NAME", "locallens")
os.environ.setdefault("JWT_SECRET", secrets.token_hex(32))

from app import app  # noqa: E402
from globals import (  # noqa: E402
    businesses_collection,
    ensure_indexes,
    reviews_collection,
)
from scripts.create_users import main as create_demo_users  # noqa: E402


class LocalLensApiSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.admin_password = os.getenv("ADMIN_PASSWORD")
        self.user_password = os.getenv("USER_PASSWORD")
        if not self.admin_password or not self.user_password:
            self.fail("ADMIN_PASSWORD and USER_PASSWORD are required")
        create_demo_users()
        ensure_indexes()
        self.client = app.test_client()
        self.created_business_id: str | None = None

    def tearDown(self) -> None:
        if self.created_business_id:
            from bson import ObjectId

            oid = ObjectId(self.created_business_id)
            reviews_collection.delete_many({"business_id": oid})
            businesses_collection.delete_one({"_id": oid})

    def auth(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    def test_end_to_end(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

        response = self.client.post(
            "/api/v1.0/login",
            json={"username": "admin", "password": self.admin_password},
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        admin_token = response.get_json()["token"]
        self.assertTrue(admin_token)

        response = self.client.get(
            "/api/v1.0/login",
            query_string={"username": "alice", "password": self.user_password},
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        user_token = response.get_json()["token"]

        response = self.client.get(
            "/api/v1.0/businesses?pn=1&ps=5&sort=-rating",
            headers={"Origin": "http://localhost:4200"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            response.headers.get("Access-Control-Allow-Origin"),
            {"*", "http://localhost:4200"},
        )
        listing = response.get_json()
        self.assertGreaterEqual(listing["total"], 120)
        self.assertEqual(len(listing["items"]), 5)

        response = self.client.get("/api/v1.0/businesses?category=Cafe&ps=5")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            all("Cafe" in item["categories"] for item in response.get_json()["items"])
        )

        response = self.client.get("/api/v1.0/businesses?pn=0")
        self.assertEqual(response.status_code, 400)

        run_id = uuid4().hex
        business_payload = {
            "name": f"Integration Cafe {run_id}",
            "town": "Belfast",
            "address": "10 Integration Street",
            "postcode": "BT1 1AA",
            "categories": ["Cafe", "Bakery"],
            "description": "Created by the end-to-end smoke test.",
            "location": {"type": "Point", "coordinates": [-5.93, 54.5973]},
            "price_level": 2,
            "active": True,
        }
        response = self.client.post("/api/v1.0/businesses", json=business_payload)
        self.assertEqual(response.status_code, 401)

        response = self.client.post(
            "/api/v1.0/businesses",
            json=business_payload,
            headers=self.auth(admin_token),
        )
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        self.created_business_id = response.get_json()["_id"]

        response = self.client.post(
            "/api/v1.0/businesses",
            json=business_payload,
            headers=self.auth(admin_token),
        )
        self.assertEqual(response.status_code, 409)

        response = self.client.get("/api/v1.0/businesses/not-an-object-id")
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            f"/api/v1.0/businesses/{self.created_business_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], business_payload["name"])

        response = self.client.put(
            f"/api/v1.0/businesses/{self.created_business_id}",
            json={"description": "Updated by the integration test.", "price_level": 3},
            headers=self.auth(admin_token),
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        self.assertEqual(response.get_json()["price_level"], 3)

        response = self.client.delete(
            f"/api/v1.0/businesses/{self.created_business_id}",
            headers=self.auth(user_token),
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            f"/api/v1.0/businesses/{self.created_business_id}/reviews",
            json={"rating": 5, "text": "Excellent smoke-test visit."},
            headers=self.auth(admin_token),
        )
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        review_id = response.get_json()["_id"]

        response = self.client.get(
            f"/api/v1.0/businesses/{self.created_business_id}/reviews/{review_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["rating"], 5)

        response = self.client.put(
            f"/api/v1.0/businesses/{self.created_business_id}/reviews/{review_id}",
            json={"rating": 4, "text": "Updated smoke-test review."},
            headers=self.auth(user_token),
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.put(
            f"/api/v1.0/businesses/{self.created_business_id}/reviews/{review_id}",
            json={"rating": 4, "text": "Updated smoke-test review."},
            headers=self.auth(admin_token),
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        self.assertEqual(response.get_json()["rating"], 4)

        response = self.client.get(
            f"/api/v1.0/businesses/{self.created_business_id}/reviews?pn=1&ps=10"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["total"], 1)

        response = self.client.get("/api/v1.0/businesses/advanced?pn=1&ps=5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["pipeline_stages"],
            ["$match", "$project", "$unwind", "$match", "$sort", "$skip", "$limit"],
        )

        response = self.client.get("/api/v1.0/businesses/stats/by-town?limit=20")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.get_json()["items"]), 0)

        response = self.client.get(
            "/api/v1.0/businesses/nearby?longitude=-5.9301&latitude=54.5973&max_distance=10000&ps=5"
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        nearby = response.get_json()["items"]
        self.assertGreater(len(nearby), 0)
        self.assertIn("distance_m", nearby[0])

        response = self.client.delete(
            f"/api/v1.0/businesses/{self.created_business_id}/reviews/{review_id}",
            headers=self.auth(admin_token),
        )
        self.assertEqual(response.status_code, 204, response.get_data(as_text=True))

        response = self.client.delete(
            f"/api/v1.0/businesses/{self.created_business_id}",
            headers=self.auth(admin_token),
        )
        self.assertEqual(response.status_code, 204, response.get_data(as_text=True))
        self.created_business_id = None

        response = self.client.get(
            "/api/v1.0/logout", headers=self.auth(admin_token)
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))

        response = self.client.get(
            "/api/v1.0/logout", headers=self.auth(admin_token)
        )
        self.assertEqual(response.status_code, 401, response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)