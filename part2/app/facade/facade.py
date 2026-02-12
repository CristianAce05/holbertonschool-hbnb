from typing import Optional, List, Dict, Any
from app.persistence.inmemory.repository import InMemoryRepository


class HBnBFacade:
    """Facade to access persistence and provide a simple business API.

    This stands in for the full Facade pattern; it will let presentation
    code call simple methods without depending on repository details.
    """

    def __init__(self, repository: Optional[InMemoryRepository] = None):
        self.repo = repository or InMemoryRepository()

    def create(self, obj) -> Dict[str, Any]:
        return self.repo.add(obj)

    def get(self, obj_id: str) -> Optional[Dict[str, Any]]:
        return self.repo.get(obj_id)

    def update(self, obj_id: str, changes: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return self.repo.update(obj_id, changes)

    def delete(self, obj_id: str) -> bool:
        return self.repo.delete(obj_id)

    def list(self) -> List[Dict[str, Any]]:
        return self.repo.list_all()
