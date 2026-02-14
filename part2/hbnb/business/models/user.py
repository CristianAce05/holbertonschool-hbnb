"""User model for HBNB."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .base import BaseModel


@dataclass
class User(BaseModel):
    email: str = ""
    password: str = ""
    first_name: str = ""
    last_name: str = ""

    def __post_init__(self):
        if not isinstance(self.email, str):
            raise TypeError("email must be a string")
        if not isinstance(self.password, str):
            raise TypeError("password must be a string")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return super().from_dict(data)
