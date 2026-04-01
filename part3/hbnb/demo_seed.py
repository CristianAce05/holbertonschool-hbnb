"""Helpers for loading demo data into the in-memory HBnB app."""

from __future__ import annotations

from typing import Any, Dict

DEMO_USER_EMAIL = "flow@example.com"
DEMO_USER_PASSWORD = "secret123"


def seed_demo_data(app) -> Dict[str, Any]:
    """Populate a fresh in-memory app with a demo user, place, and review.

    The seed is idempotent for the demo email so repeated calls on the same
    process do not duplicate data.
    """

    facade = app.extensions.get("hbnb_facade")
    if facade is None:
        raise RuntimeError("The app does not expose an HBNB facade for seeding.")

    for user in facade.list("User"):
        if user.get("email") == DEMO_USER_EMAIL:
            place = _find_first_place_for_user(facade, user.get("id"))
            return {
                "seeded": False,
                "user": _sanitize_user(user),
                "place": place,
                "credentials": {
                    "email": DEMO_USER_EMAIL,
                    "password": DEMO_USER_PASSWORD,
                },
            }

    user = facade.create(
        "User",
        {
            "first_name": "Flow",
            "last_name": "Tester",
            "email": DEMO_USER_EMAIL,
            "password": DEMO_USER_PASSWORD,
        },
    )

    wifi = facade.create("Amenity", {"name": "Fast Wi-Fi"})
    coffee = facade.create("Amenity", {"name": "Coffee station"})
    pool = facade.create("Amenity", {"name": "Swimming Pool"})
    parking = facade.create("Amenity", {"name": "Free Parking"})
    kitchen = facade.create("Amenity", {"name": "Full Kitchen"})
    ac = facade.create("Amenity", {"name": "Air Conditioning"})

    place1 = facade.create(
        "Place",
        {
            "user_id": user["id"],
            "name": "Sunny Beach House",
            "description": "A bright and airy beach house just steps from the sand. "
            "Perfect for a relaxing getaway with ocean views from every room.",
            "country": "Uruguay",
            "price_by_night": 120,
            "number_rooms": 3,
            "number_bathrooms": 2,
            "max_guest": 6,
            "amenity_ids": [wifi["id"], pool["id"], parking["id"], kitchen["id"]],
            "image": "images/place_beach.jpg",
        },
    )

    place2 = facade.create(
        "Place",
        {
            "user_id": user["id"],
            "name": "Downtown Loft",
            "description": "Modern loft in the heart of the city with exposed brick walls, "
            "high ceilings, and walking distance to restaurants and nightlife.",
            "country": "Argentina",
            "price_by_night": 85,
            "number_rooms": 1,
            "number_bathrooms": 1,
            "max_guest": 2,
            "amenity_ids": [wifi["id"], coffee["id"], ac["id"]],
            "image": "images/place_loft.jpg",
        },
    )

    place3 = facade.create(
        "Place",
        {
            "user_id": user["id"],
            "name": "Mountain Cabin Retreat",
            "description": "Cozy wooden cabin surrounded by pine trees with a fireplace, "
            "hiking trails nearby, and stunning mountain views.",
            "country": "Chile",
            "price_by_night": 95,
            "number_rooms": 2,
            "number_bathrooms": 1,
            "max_guest": 4,
            "amenity_ids": [wifi["id"], parking["id"], kitchen["id"]],
            "image": "images/place_cabin.jpg",
        },
    )

    place4 = facade.create(
        "Place",
        {
            "user_id": user["id"],
            "name": "Colonial Garden Suite",
            "description": "Charming suite in a restored colonial home with a private garden, "
            "hammock, and traditional tile floors.",
            "country": "Colombia",
            "price_by_night": 70,
            "number_rooms": 1,
            "number_bathrooms": 1,
            "max_guest": 2,
            "amenity_ids": [wifi["id"], coffee["id"], ac["id"]],
            "image": "images/place_colonial.jpg",
        },
    )

    place5 = facade.create(
        "Place",
        {
            "user_id": user["id"],
            "name": "Lakefront Villa",
            "description": "Spacious villa on the lake with a private dock, kayaks included, "
            "and panoramic sunset views from the terrace.",
            "country": "Uruguay",
            "price_by_night": 200,
            "number_rooms": 4,
            "number_bathrooms": 3,
            "max_guest": 8,
            "amenity_ids": [wifi["id"], pool["id"], parking["id"], kitchen["id"], ac["id"]],
            "image": "images/place_lake.jpg",
        },
    )

    review = facade.create(
        "Review",
        {
            "user_id": user["id"],
            "place_id": place1["id"],
            "text": "Amazing stay! The beach was gorgeous and the house was spotless.",
        },
    )

    facade.create(
        "Review",
        {
            "user_id": user["id"],
            "place_id": place2["id"],
            "text": "Great location right in the city center. Loved the brick walls and the coffee shops nearby.",
        },
    )

    facade.create(
        "Review",
        {
            "user_id": user["id"],
            "place_id": place3["id"],
            "text": "So peaceful and quiet. Woke up to birds singing and had coffee on the porch with mountain views.",
        },
    )

    facade.create(
        "Review",
        {
            "user_id": user["id"],
            "place_id": place4["id"],
            "text": "Beautiful colonial charm. The garden was a lovely surprise and the hammock was perfect for afternoon naps.",
        },
    )

    facade.create(
        "Review",
        {
            "user_id": user["id"],
            "place_id": place5["id"],
            "text": "Incredible sunsets from the terrace. We used the kayaks every morning. Worth every penny.",
        },
    )

    return {
        "seeded": True,
        "user": _sanitize_user(user),
        "place": place1,
        "review": review,
        "credentials": {
            "email": DEMO_USER_EMAIL,
            "password": DEMO_USER_PASSWORD,
        },
    }


def _find_first_place_for_user(facade, user_id: str | None):
    if not user_id:
        return None
    for place in facade.list("Place"):
        if place.get("user_id") == user_id:
            return place
    return None


def _sanitize_user(user: Dict[str, Any] | None):
    if user is None:
        return None
    result = dict(user)
    result.pop("password", None)
    return result
