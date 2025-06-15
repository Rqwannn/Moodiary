from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, Mapped

from uuid import UUID

if TYPE_CHECKING:
    from app.Models.user import User

class Note(SQLModel, table=True):
    __tablename__ = "Notes"

    uuid: UUID = Field(primary_key=True, index=True)
    id_user: str = Field(unique=True)

    createdAt: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = Field(default_factory=datetime.now(timezone.utc))

    # Relationships
    user: Optional["User"] = Relationship(back_populates="notes_list")

    def to_dict(self):
        result = {}
        for col in self.__table__.columns:
            if col.name in ['createdAt', 'updatedAt']:
                continue
            result[col.name] = getattr(self, col.name)

        try:
            if self.notes_list:
                result["notes"] = [note.to_dict() for note in self.notes_list]
        except Exception as e:
            print(e)
            pass

        return result