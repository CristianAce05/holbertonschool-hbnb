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

    place = facade.create(
        "Place",
        {
            "user_id": user["id"],
            "name": "Flow Test Loft",
            "description": "Preloaded demo place for frontend walkthroughs.",
            "price_by_night": 88,
            "number_rooms": 1,
            "number_bathrooms": 1,
            "max_guest": 2,
            "amenity_ids": [wifi["id"], coffee["id"]],
        },
    )

    review = facade.create(
        "Review",
        {
            "user_id": user["id"],
            "place_id": place["id"],
            "text": "Demo review loaded automatically on startup.",
        },
    )

    return {
        "seeded": True,
        "user": _sanitize_user(user),
        "place": place,
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