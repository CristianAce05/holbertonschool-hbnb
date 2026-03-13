"""Persistence layer package for HBNB app.

This package exposes repository implementations. Use `InMemoryRepository`
for fast in-memory testing, or `SQLAlchemyRepository` for persistence
once the database schema is initialized.
"""

from .in_memory_repository import InMemoryRepository
from .sqlalchemy_repository import SQLAlchemyRepository

__all__ = ["InMemoryRepository", "SQLAlchemyRepository"]
