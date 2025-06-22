from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, Mapped

from uuid import UUID

if TYPE_CHECKING:
    from app.Models.note_emotions import NoteEmotion 
    from app.Models.user import User 

class NotesBase(SQLModel):
    title: str = Field(max_length=200)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Notes(NotesBase, table=True):
    __tablename__ = "notes"
    
    id_notes: Optional[int] = Field(default=None, primary_key=True)
    id_user: UUID = Field(foreign_key="users.uid")
    title: str = Field(max_length=200)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Relations
    user: Optional["User"] = Relationship(back_populates="notes_list")
    note_emotions: Optional[List["NoteEmotion"]] = Relationship(back_populates="note")

    def to_dict(self):
        result = {}
        for col in self.__table__.columns:
            if col.name in ['createdAt', 'updatedAt']:
                continue
            result[col.name] = getattr(self, col.name)

        try:
            if self.note_emotions:
                result["notes_emotions"] = [result.to_dict() for result in self.note_emotions]
        except Exception as e:
            print(e)
            pass

        return result