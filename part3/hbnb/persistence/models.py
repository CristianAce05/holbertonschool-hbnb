"""SQLAlchemy ORM models for HBNB persistence.

This module defines a shared declarative `Base` and mapped classes for
the domain entities. Table creation is intentionally left to the
initialization/migration step handled elsewhere.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
    Integer,
    Float,
    Text,
)

Base = declarative_base()


def _now_dt():
    return datetime.now(timezone.utc)


class BaseModelMixin:
    id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_now_dt)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=_now_dt, onupdate=_now_dt
    )

    def to_dict(self) -> Dict[str, Any]:
        # Used by repositories to convert ORM objects to dicts
        out = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Normalize datetimes to ISO Z
        if out.get("created_at"):
            out["created_at"] = (
                out["created_at"]
                .astimezone(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            )
        if out.get("updated_at"):
            out["updated_at"] = (
                out["updated_at"]
                .astimezone(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            )
        return out


class User(Base, BaseModelMixin):
    __tablename__ = "users"
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    # relationships
    places = relationship("Place", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )


class Place(Base, BaseModelMixin):
    __tablename__ = "places"
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    number_rooms = Column(Integer, nullable=True)
    number_bathrooms = Column(Integer, nullable=True)
    max_guest = Column(Integer, nullable=True)
    price_by_night = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    # relationship to owner
    user = relationship("User", back_populates="places")
    # reviews relationship
    reviews = relationship(
        "Review", back_populates="place", cascade="all, delete-orphan"
    )
    # amenities: many-to-many via association table added below
    amenities = relationship(
        "Amenity", secondary=lambda: place_amenity_table, back_populates="places"
    )


class Review(Base, BaseModelMixin):
    __tablename__ = "reviews"
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    place_id = Column(String, ForeignKey("places.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    # relationships
    user = relationship("User", back_populates="reviews")
    place = relationship("Place", back_populates="reviews")


class Amenity(Base, BaseModelMixin):
    __tablename__ = "amenities"
    name = Column(String, nullable=False)
    # places many-to-many
    places = relationship(
        "Place", secondary=lambda: place_amenity_table, back_populates="amenities"
    )


# Association table for Place <-> Amenity many-to-many
place_amenity_table = Table(
    "place_amenity",
    Base.metadata,
    Column("place_id", String, ForeignKey("places.id"), primary_key=True),
    Column("amenity_id", String, ForeignKey("amenities.id"), primary_key=True),
)
