"""User model for HBNB with password hashing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .base import BaseModel

import bcrypt


@dataclass
class User(BaseModel):
    email: str = ""
    password: str = ""
    first_name: str = ""
    last_name: str = ""
    is_admin: bool = False

    def __post_init__(self):
        if not isinstance(self.email, str):
            raise TypeError("email must be a string")
        if not isinstance(self.password, str):
            raise TypeError("password must be a string")
        if not isinstance(self.is_admin, bool):
            raise TypeError("is_admin must be a boolean")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        # Create instance from known fields
        inst = super().from_dict(data)
        # If a raw password was provided in data, hash it before storing
        if isinstance(data, dict) and data.get("password"):
            raw = data.get("password")
            if isinstance(raw, str) and raw:
                hashed = bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt())
                inst.password = hashed.decode("utf-8")
        # copy is_admin if provided
        if isinstance(data, dict) and "is_admin" in data:
            try:
                inst.is_admin = bool(data.get("is_admin"))
            except Exception:
                inst.is_admin = False
        return inst

    def to_dict(self) -> Dict[str, Any]:
        # Exclude password from serialized representation
        d = super().to_dict()
        d.pop("password", None)
        return d

    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        # Ensure password is hashed when updated
        pwd = updates.get("password")
        if isinstance(pwd, str) and pwd:
            hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
            updates = dict(updates)
            updates["password"] = hashed.decode("utf-8")
        super().update_from_dict(updates)
