"""Amenity repository implemented with SQLAlchemy ORM."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from .models import Amenity as ORMAmenity


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class AmenityRepository:
    def __init__(self, database_uri: str = "sqlite:///hbnb_dev.db", echo: bool = False):
        self._engine = create_engine(database_uri, echo=echo, future=True)
        self._Session = sessionmaker(bind=self._engine, future=True)

    def _session(self):
        return self._Session()

    def create(self, cls_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        session = self._session()
        try:
            u = ORMAmenity()
            u.name = payload.get("name") or ""
            now = _now_iso()
            u.created_at = u.updated_at = datetime.fromisoformat(now.replace("Z", "+00:00"))
            session.add(u)
            session.commit()
            return u.to_dict()
        finally:
            session.close()

    def get(self, cls_name: str, obj_id: str) -> Optional[Dict[str, Any]]:
        session = self._session()
        try:
            stmt = select(ORMAmenity).where(ORMAmenity.id == obj_id)
            row = session.execute(stmt).scalars().first()
            return deepcopy(row.to_dict()) if row else None
        finally:
            session.close()

    def list(self, cls_name: str) -> List[Dict[str, Any]]:
        session = self._session()
        try:
            stmt = select(ORMAmenity)
            rows = session.execute(stmt).scalars().all()
            return [deepcopy(r.to_dict()) for r in rows]
        finally:
            session.close()

    def update(self, cls_name: str, obj_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = self._session()
        try:
            stmt = select(ORMAmenity).where(ORMAmenity.id == obj_id)
            row = session.execute(stmt).scalars().first()
            if row is None:
                return None
            for k, v in updates.items():
                if k in ("id", "created_at"):
                    continue
                if hasattr(row, k):
                    setattr(row, k, v)
            row.updated_at = datetime.fromisoformat(_now_iso().replace("Z", "+00:00"))
            session.add(row)
            session.commit()
            return deepcopy(row.to_dict())
        finally:
            session.close()

    def delete(self, cls_name: str, obj_id: str) -> bool:
        session = self._session()
        try:
            stmt = select(ORMAmenity).where(ORMAmenity.id == obj_id)
            row = session.execute(stmt).scalars().first()
            if row is None:
                return False
            session.delete(row)
            session.commit()
            return True
        finally:
            session.close()

    def list_all(self) -> Dict[str, List[Dict[str, Any]]]:
        session = self._session()
        try:
            stmt = select(ORMAmenity)
            rows = session.execute(stmt).scalars().all()
            return {"Amenity": [deepcopy(r.to_dict()) for r in rows]}
        finally:
            session.close()

    def count(self, cls_name: str) -> int:
        session = self._session()
        try:
            stmt = select(ORMAmenity)
            rows = session.execute(stmt).scalars().all()
            return len(rows)
        finally:
            session.close()
