from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, TYPE_CHECKING, Any
from datetime import datetime, timezone
from sqlalchemy.orm import relationship, Mapped

from uuid import UUID

if TYPE_CHECKING:
    from app.Models.emotions import Emotion

class RecommendationBase(SQLModel):
    recc_text: str

class Recommendation(RecommendationBase, table=True):
    __tablename__ = "recommendations"
    
    id_recc: Optional[int] = Field(default=None, primary_key=True)
    id_emotion: int = Field(foreign_key="emotions.id_emotion")
    recc_text: str = Field(max_length=255)
    
    # Relationships
    emotion: Optional["Emotion"] = Relationship(back_populates="recommendations")

    def to_dict(self):
        return {
            'id_recc': self.id_recc,
            'id_emotion': self.id_emotion,
            'recc_text': self.recc_text
        }
    
    def to_dict_with_relations(self, include_emotion: bool = False) -> Dict[str, Any]:
        result = {
            'id_recc': self.id_recc,
            'id_emotion': self.id_emotion,
            'recc_text': self.recc_text
        }
        
        if include_emotion and self.emotion:
            result['emotion'] = {
                'id_emotion': self.emotion.id_emotion,
                'tipe_emosi': self.emotion.tipe_emosi
            }
        
        return result
