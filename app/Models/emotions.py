from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, Mapped

from uuid import UUID

if TYPE_CHECKING:
    from app.Models.recomendastions import Recommendation
    from app.Models.note_emotions import NoteEmotion

class EmotionBase(SQLModel):
    tipe_emosi: str = Field(max_length=50)

class Emotion(EmotionBase, table=True):
    __tablename__ = "emotions"
    
    id_emotion: Optional[int] = Field(default=None, primary_key=True)
    tipe_emosi: str = Field(max_length=50)
    
    # Relationships
    recommendations: List["Recommendation"] = Relationship(back_populates="emotion")
    note_emotions: List["NoteEmotion"] = Relationship(back_populates="emotion")

    def to_dict(self):
        result = {}
        for col in self.__table__.columns:
            if col.name in ['createdAt', 'updatedAt']:
                continue
            result[col.name] = getattr(self, col.name)

        try:
            if self.recommendations:
                result["recomendations"] = [result.to_dict() for result in self.recommendations]
        except Exception as e:
            pass
        
        try:
            if self.note_emotions:
                result["note_emotions"] = [result.to_dict() for result in self.note_emotions]
        except Exception as e:
            pass

        return result