"""Composite repository that routes User operations to UserRepository and
falls back to a generic repository for other classes.
"""

from __future__ import annotations

from typing import Any, Dict


class CompositeRepository:
    def __init__(
        self,
        user_repo,
        generic_repo,
        place_repo=None,
        review_repo=None,
        amenity_repo=None,
    ):
        self.user_repo = user_repo
        self.generic_repo = generic_repo
        self.place_repo = place_repo
        self.review_repo = review_repo
        self.amenity_repo = amenity_repo

    def create(self, cls_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if cls_name == "User":
            return self.user_repo.create(cls_name, payload)
        if cls_name == "Place" and self.place_repo is not None:
            return self.place_repo.create(cls_name, payload)
        if cls_name == "Review" and self.review_repo is not None:
            return self.review_repo.create(cls_name, payload)
        if cls_name == "Amenity" and self.amenity_repo is not None:
            return self.amenity_repo.create(cls_name, payload)
        return self.generic_repo.create(cls_name, payload)

    def get(self, cls_name: str, obj_id: str):
        if cls_name == "User":
            return self.user_repo.get(cls_name, obj_id)
        if cls_name == "Place" and self.place_repo is not None:
            return self.place_repo.get(cls_name, obj_id)
        if cls_name == "Review" and self.review_repo is not None:
            return self.review_repo.get(cls_name, obj_id)
        if cls_name == "Amenity" and self.amenity_repo is not None:
            return self.amenity_repo.get(cls_name, obj_id)
        return self.generic_repo.get(cls_name, obj_id)

    def list(self, cls_name: str):
        if cls_name == "User":
            return self.user_repo.list(cls_name)
        if cls_name == "Place" and self.place_repo is not None:
            return self.place_repo.list(cls_name)
        if cls_name == "Review" and self.review_repo is not None:
            return self.review_repo.list(cls_name)
        if cls_name == "Amenity" and self.amenity_repo is not None:
            return self.amenity_repo.list(cls_name)
        return self.generic_repo.list(cls_name)

    def update(self, cls_name: str, obj_id: str, updates: Dict[str, Any]):
        if cls_name == "User":
            return self.user_repo.update(cls_name, obj_id, updates)
        if cls_name == "Place" and self.place_repo is not None:
            return self.place_repo.update(cls_name, obj_id, updates)
        if cls_name == "Review" and self.review_repo is not None:
            return self.review_repo.update(cls_name, obj_id, updates)
        if cls_name == "Amenity" and self.amenity_repo is not None:
            return self.amenity_repo.update(cls_name, obj_id, updates)
        return self.generic_repo.update(cls_name, obj_id, updates)

    def delete(self, cls_name: str, obj_id: str):
        if cls_name == "User":
            return self.user_repo.delete(cls_name, obj_id)
        if cls_name == "Place" and self.place_repo is not None:
            return self.place_repo.delete(cls_name, obj_id)
        if cls_name == "Review" and self.review_repo is not None:
            return self.review_repo.delete(cls_name, obj_id)
        if cls_name == "Amenity" and self.amenity_repo is not None:
            return self.amenity_repo.delete(cls_name, obj_id)
        return self.generic_repo.delete(cls_name, obj_id)

    def clear(self):
        try:
            self.user_repo.clear()
        except Exception:
            pass
        try:
            self.generic_repo.clear()
        except Exception:
            pass

    def list_all(self):
        out = {}
        try:
            out.update(self.generic_repo.list_all())
        except Exception:
            pass
        try:
            out.update(self.user_repo.list_all())
        except Exception:
            pass
        try:
            if self.place_repo is not None:
                out.update(self.place_repo.list_all())
        except Exception:
            pass
        try:
            if self.review_repo is not None:
                out.update(self.review_repo.list_all())
        except Exception:
            pass
        try:
            if self.amenity_repo is not None:
                out.update(self.amenity_repo.list_all())
        except Exception:
            pass
        return out

    def count(self, cls_name: str):
        if cls_name == "User":
            return self.user_repo.count(cls_name)
        if cls_name == "Place" and self.place_repo is not None:
            return self.place_repo.count(cls_name)
        if cls_name == "Review" and self.review_repo is not None:
            return self.review_repo.count(cls_name)
        if cls_name == "Amenity" and self.amenity_repo is not None:
            return self.amenity_repo.count(cls_name)
        return self.generic_repo.count(cls_name)
