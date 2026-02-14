"""Review model for HBNB."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base import BaseModel


@dataclass
class Review(BaseModel):
    user_id: str = ""
    place_id: str = ""
    text: str = ""

    def __post_init__(self):
        if not isinstance(self.user_id, str):
            raise TypeError("user_id must be a string")
        if not isinstance(self.place_id, str):
            raise TypeError("place_id must be a string")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Review":
        return super().from_dict(data)
