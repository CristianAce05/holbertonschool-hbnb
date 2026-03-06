"""Simple in-memory repository for storing objects during Part 2.

This repository stores objects as dicts keyed by class name and id.
It is intentionally lightweight so it can be swapped for a DB-backed
repository in Part 3 with minimal changes to the facade.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import uuid
from typing import Dict, Any, List


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


def _now_iso() -> str:
    # Use timezone-aware UTC timestamps and keep the trailing Z for compatibility
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class InMemoryRepository:
    def __init__(self) -> None:
        # storage: {cls_name: {id: obj_dict}}
        self._data: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def _ensure_cls(self, cls_name: str) -> None:
        if cls_name not in self._data:
            self._data[cls_name] = {}

    def _generate_id(self) -> str:
        return uuid.uuid4().hex

    def create(self, cls_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValidationError("payload must be a dict")

        self._ensure_cls(cls_name)
        obj_id = self._generate_id()
        now = _now_iso()
        obj = deepcopy(payload)
        obj.pop("id", None)
        obj["id"] = obj_id
        obj["created_at"] = now
        obj["updated_at"] = now
        self._data[cls_name][obj_id] = obj
        return deepcopy(obj)

    def get(self, cls_name: str, obj_id: str) -> Dict[str, Any] | None:
        self._ensure_cls(cls_name)
        obj = self._data[cls_name].get(obj_id)
        return deepcopy(obj) if obj is not None else None

    def list(self, cls_name: str) -> List[Dict[str, Any]]:
        self._ensure_cls(cls_name)
        return [deepcopy(v) for v in self._data[cls_name].values()]

    def update(self, cls_name: str, obj_id: str, updates: Dict[str, Any]) -> Dict[str, Any] | None:
        if not isinstance(updates, dict):
            raise ValidationError("updates must be a dict")
        self._ensure_cls(cls_name)
        if obj_id not in self._data[cls_name]:
            return None
        obj = self._data[cls_name][obj_id]
        for k, v in updates.items():
            if k in ("id", "created_at"):
                continue
            obj[k] = deepcopy(v)
        obj["updated_at"] = _now_iso()
        return deepcopy(obj)

    def delete(self, cls_name: str, obj_id: str) -> bool:
        self._ensure_cls(cls_name)
        if obj_id in self._data[cls_name]:
            del self._data[cls_name][obj_id]
            return True
        return False

    def clear(self) -> None:
        self._data.clear()

    def list_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return all stored objects grouped by class name."""
        return {k: [deepcopy(v) for v in vals.values()] for k, vals in self._data.items()}

    def count(self, cls_name: str) -> int:
        """Return number of instances for a given class."""
        self._ensure_cls(cls_name)
        return len(self._data[cls_name])
