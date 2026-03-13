"""SQLAlchemy-based repository implementation for HBNB.

This repository implements the same interface as `InMemoryRepository` but
persists objects in a simple generic table using SQLAlchemy. Each stored
object is keyed by `cls_name` and `id`, and the object payload is stored
in a JSON column. This allows the application to persist arbitrary
resource dicts before full ORM model mapping is introduced.

Important: This class intentionally does NOT call `Base.metadata.create_all()`
or otherwise initialize the database schema. Table creation and DB
initialization should be performed in the next task to avoid accidental
initialization during code changes.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import uuid
from typing import Dict, Any, List, Optional

from sqlalchemy import (
    Column,
    String,
    JSON,
    DateTime,
    create_engine,
    select,
)
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ObjectStore(Base):
    __tablename__ = "objects"
    id = Column(String, primary_key=True)
    cls_name = Column(String, index=True, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class SQLAlchemyRepository:
    """A simple repository backed by SQLAlchemy.

    Note: table creation is not performed here. Callers should create the
    required tables when ready.
    """

    def __init__(self, database_uri: str = "sqlite:///hbnb_dev.db", echo: bool = False):
        self._engine = create_engine(database_uri, echo=echo, future=True)
        self._Session = sessionmaker(bind=self._engine, future=True)

    def _ensure_session(self):
        return self._Session()

    def _generate_id(self) -> str:
        return uuid.uuid4().hex

    def create(self, cls_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict")
        session = self._ensure_session()
        try:
            obj_id = self._generate_id()
            now = _now_iso()
            data = deepcopy(payload)
            data.pop("id", None)
            data["id"] = obj_id
            data["created_at"] = now
            data["updated_at"] = now
            row = ObjectStore(
                id=obj_id,
                cls_name=cls_name,
                data=data,
                created_at=datetime.fromisoformat(now.replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(now.replace("Z", "+00:00")),
            )
            session.add(row)
            session.commit()
            return deepcopy(data)
        finally:
            session.close()

    def get(self, cls_name: str, obj_id: str) -> Optional[Dict[str, Any]]:
        session = self._ensure_session()
        try:
            stmt = select(ObjectStore).where(ObjectStore.cls_name == cls_name, ObjectStore.id == obj_id)
            res = session.execute(stmt).scalars().first()
            if res is None:
                return None
            return deepcopy(res.data)
        finally:
            session.close()

    def list(self, cls_name: str) -> List[Dict[str, Any]]:
        session = self._ensure_session()
        try:
            stmt = select(ObjectStore).where(ObjectStore.cls_name == cls_name)
            rows = session.execute(stmt).scalars().all()
            return [deepcopy(r.data) for r in rows]
        finally:
            session.close()

    def update(self, cls_name: str, obj_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(updates, dict):
            raise ValueError("updates must be a dict")
        session = self._ensure_session()
        try:
            stmt = select(ObjectStore).where(ObjectStore.cls_name == cls_name, ObjectStore.id == obj_id)
            row = session.execute(stmt).scalars().first()
            if row is None:
                return None
            data = dict(row.data)
            for k, v in updates.items():
                if k in ("id", "created_at"):
                    continue
                data[k] = deepcopy(v)
            data["updated_at"] = _now_iso()
            row.data = data
            row.updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            session.add(row)
            session.commit()
            return deepcopy(data)
        finally:
            session.close()

    def delete(self, cls_name: str, obj_id: str) -> bool:
        session = self._ensure_session()
        try:
            stmt = select(ObjectStore).where(ObjectStore.cls_name == cls_name, ObjectStore.id == obj_id)
            row = session.execute(stmt).scalars().first()
            if row is None:
                return False
            session.delete(row)
            session.commit()
            return True
        finally:
            session.close()

    def clear(self) -> None:
        session = self._ensure_session()
        try:
            session.query(ObjectStore).delete()
            session.commit()
        finally:
            session.close()

    def list_all(self) -> Dict[str, List[Dict[str, Any]]]:
        session = self._ensure_session()
        try:
            stmt = select(ObjectStore)
            rows = session.execute(stmt).scalars().all()
            out: Dict[str, List[Dict[str, Any]]] = {}
            for r in rows:
                out.setdefault(r.cls_name, []).append(deepcopy(r.data))
            return out
        finally:
            session.close()

    def count(self, cls_name: str) -> int:
        session = self._ensure_session()
        try:
            stmt = select(ObjectStore).where(ObjectStore.cls_name == cls_name)
            rows = session.execute(stmt).scalars().all()
            return len(rows)
        finally:
            session.close()
