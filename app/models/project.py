from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ProjectDTO:
    id: str
    owner_id: str
    name: str
    description: str
    created_at: Optional[datetime]
    status: str

    @staticmethod
    def from_firestore(doc) -> "ProjectDTO":
        data = doc.to_dict()

        # Safety check for missing fields to prevent crashes
        return ProjectDTO(
            id=doc.id,
            owner_id=data.get("owner_id"),
            name=data.get("name", "Untitled"),
            description=data.get("description", ""),
            created_at=data.get("created_at"),
            status=data.get("status", "draft"),
        )
