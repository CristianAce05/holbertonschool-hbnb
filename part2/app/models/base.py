import uuid
from datetime import datetime


class BaseModel:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id') or str(uuid.uuid4())
        now = datetime.utcnow()
        self.created_at = kwargs.get('created_at') or now
        self.updated_at = kwargs.get('updated_at') or now

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at,
            'updated_at': self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
