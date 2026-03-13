"""SQLAlchemy ORM models for HBNB persistence.

This module defines a shared declarative `Base` and mapped classes for
the domain entities. Table creation is intentionally left to the
initialization/migration step handled elsewhere.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Boolean, DateTime, JSON


Base = declarative_base()


def _now_dt():
    return datetime.now(timezone.utc)


class BaseModelMixin:
    id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        # Used by repositories to convert ORM objects to dicts
        out = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Normalize datetimes to ISO Z
        if out.get("created_at"):
            out["created_at"] = out["created_at"].astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        if out.get("updated_at"):
            out["updated_at"] = out["updated_at"].astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        return out


class User(Base, BaseModelMixin):
    __tablename__ = "users"
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)


class Place(Base, BaseModelMixin):
    __tablename__ = "places"
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    number_rooms = Column(String, nullable=True)
    number_bathrooms = Column(String, nullable=True)
    max_guest = Column(String, nullable=True)
    price_by_night = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    user_id = Column(String, nullable=True, index=True)
    amenity_ids = Column(JSON, default=list, nullable=True)


class Review(Base, BaseModelMixin):
    __tablename__ = "reviews"
    user_id = Column(String, nullable=False, index=True)
    place_id = Column(String, nullable=False, index=True)
    text = Column(String, nullable=False)


class Amenity(Base, BaseModelMixin):
    __tablename__ = "amenities"
    name = Column(String, nullable=False)
