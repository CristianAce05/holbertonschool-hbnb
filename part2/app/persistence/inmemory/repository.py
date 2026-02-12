from typing import Dict, Any, List, Optional
from copy import deepcopy
from app.models.base import BaseModel


class InMemoryRepository:
    """A simple in-memory repository for BaseModel-like objects.

    Stores items in a dict keyed by `id`. Accepts model instances or plain dicts.
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def _ensure_dict(self, obj) -> Dict[str, Any]:
        if isinstance(obj, BaseModel):
            return obj.to_dict()
        if isinstance(obj, dict):
            return deepcopy(obj)
        raise TypeError('Object must be a BaseModel or dict')

    def add(self, obj) -> Dict[str, Any]:
        data = self._ensure_dict(obj)
        if 'id' not in data or not data['id']:
            raise ValueError('Object must have an id')
        data['created_at'] = data.get('created_at') or data['created_at']
        data['updated_at'] = data.get('updated_at') or data['updated_at']
        self._store[data['id']] = deepcopy(data)
        return deepcopy(self._store[data['id']])

    def get(self, obj_id: str) -> Optional[Dict[str, Any]]:
        item = self._store.get(obj_id)
        return deepcopy(item) if item is not None else None

    def update(self, obj_id: str, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if obj_id not in self._store:
            return None
        self._store[obj_id].update(changes)
        self._store[obj_id]['updated_at'] = changes.get('updated_at') or self._store[obj_id]['updated_at']
        return deepcopy(self._store[obj_id])

    def delete(self, obj_id: str) -> bool:
        return self._store.pop(obj_id, None) is not None

    def list_all(self) -> List[Dict[str, Any]]:
        return [deepcopy(v) for v in self._store.values()]

    def exists(self, obj_id: str) -> bool:
        return obj_id in self._store
