"""Amenity model for HBNB."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseModel


@dataclass
class Amenity(BaseModel):
    name: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Amenity":
        return super().from_dict(data)
