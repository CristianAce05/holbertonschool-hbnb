"""Facade providing a simple API for business operations over repositories.

This facade uses the concrete business models when available to validate
create/update payloads while keeping repository storage decoupled.
"""
from typing import Any, Dict, List, Optional

from .models import User, Place, Review, Amenity


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


_MODEL_MAP = {
    "User": User,
    "Place": Place,
    "Review": Review,
    "Amenity": Amenity,
}


class HBNBFacade:
    def __init__(self, repository):
        self._repo = repository

    def _as_model(self, cls_name: str, data: Optional[dict]) -> Optional[object]:
        if data is None:
            return None
        model_cls = _MODEL_MAP.get(cls_name)
        if model_cls is None:
            return data
        return model_cls.from_dict(data)

    def _to_dict(self, instance_or_dict: Any) -> Dict[str, Any]:
        if hasattr(instance_or_dict, "to_dict"):
            return instance_or_dict.to_dict()
        return dict(instance_or_dict)

    def create(self, cls_name: str, payload: dict) -> dict:
        if not isinstance(payload, dict):
            raise ValidationError("payload must be a dict")
        model_cls = _MODEL_MAP.get(cls_name)
        if model_cls:
            inst = model_cls.from_dict(payload)
            data = inst.to_dict()
        else:
            data = payload
        return self._repo.create(cls_name, data)

    def get(self, cls_name: str, obj_id: str) -> dict:
        obj = self._repo.get(cls_name, obj_id)
        if obj is None:
            raise NotFoundError(f"{cls_name} {obj_id} not found")
        return obj

    def list(self, cls_name: str) -> List[Dict[str, Any]]:
        return self._repo.list(cls_name)

    def list_all(self) -> Dict[str, List[Dict[str, Any]]]:
        return self._repo.list_all()

    def count(self, cls_name: str) -> int:
        return self._repo.count(cls_name)

    def update(self, cls_name: str, obj_id: str, updates: dict) -> dict:
        if not isinstance(updates, dict):
            raise ValidationError("updates must be a dict")
        model_cls = _MODEL_MAP.get(cls_name)
        if model_cls:
            existing = self._repo.get(cls_name, obj_id)
            if existing is None:
                raise NotFoundError(f"{cls_name} {obj_id} not found")
            inst = model_cls.from_dict(existing)
            inst.update_from_dict(updates)
            validated = inst.to_dict()
            obj = self._repo.update(cls_name, obj_id, validated)
        else:
            obj = self._repo.update(cls_name, obj_id, updates)
        if obj is None:
            raise NotFoundError(f"{cls_name} {obj_id} not found")
        return obj

    def delete(self, cls_name: str, obj_id: str) -> None:
        res = self._repo.delete(cls_name, obj_id)
        if not res:
            raise NotFoundError(f"{cls_name} {obj_id} not found")
