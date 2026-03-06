"""Place model for HBNB."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .base import BaseModel


@dataclass
class Place(BaseModel):
    name: str = ""
    description: str = ""
    user_id: str = ""
    number_rooms: int = 0
    number_bathrooms: int = 0
    max_guest: int = 0
    price_by_night: int = 0
    latitude: float | None = None
    longitude: float | None = None
    amenity_ids: List[str] = field(default_factory=list)

    def __post_init__(self):
        for attr in ("number_rooms", "number_bathrooms", "max_guest", "price_by_night"):
            val = getattr(self, attr)
            if not isinstance(val, int):
                raise TypeError(f"{attr} must be int")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Place":
        return super().from_dict(data)
