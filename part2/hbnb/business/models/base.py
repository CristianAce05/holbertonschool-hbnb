"""Base model for HBNB business entities."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict
import uuid


def _now_iso() -> str:
    # Use timezone-aware UTC timestamps and keep the trailing Z for compatibility
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class BaseModel:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        # Allow subclasses to pass through unknown fields via dataclass
        # Construct with only known fields
        fields = {f.name for f in cls.__dataclass_fields__.values()} if hasattr(cls, "__dataclass_fields__") else set()
        kw = {k: v for k, v in data.items() if k in fields}
        return cls(**kw)

    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        for k, v in updates.items():
            if k in ("id", "created_at"):
                continue
            if hasattr(self, k):
                setattr(self, k, v)
        self.updated_at = _now_iso()
