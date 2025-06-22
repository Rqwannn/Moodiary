from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, Dict, TYPE_CHECKING, Any

from uuid import UUID

if TYPE_CHECKING:
    from app.Models.notes import Notes
    from app.Models.emotions import Emotion

class NoteEmotionBase(SQLModel):
    pass

class NoteEmotion(NoteEmotionBase, table=True):
    __tablename__ = "note_emotions"
    
    id_noteEmotions: Optional[int] = Field(default=None, primary_key=True)
    id_notes: int = Field(foreign_key="notes.id_notes")
    id_emotion: int = Field(foreign_key="emotions.id_emotion")
    
    # Relationships
    note: Optional["Notes"] = Relationship(back_populates="note_emotions")
    emotion: Optional["Emotion"] = Relationship(back_populates="note_emotions")

    def to_dict(self):
        return {
            'id_noteEmotions': self.id_noteEmotions,
            'id_notes': self.id_notes,
            'id_emotion': self.id_emotion
        }
    
    def to_dict_with_relations(self, include_note: bool = False, include_emotion: bool = False) -> Dict[str, Any]:
        result = {
            'id_noteEmotions': self.id_noteEmotions,
            'id_notes': self.id_notes,
            'id_emotion': self.id_emotion
        }

        if include_note and self.note:
            # Hanya ambil field penting dari note untuk menghindari circular reference
            result['note'] = {
                'id_notes': self.note.id_notes,
                'title': self.note.title,
                'content': self.note.content,
                'created_at': self.note.created_at.isoformat() if self.note.created_at else None,
                'updated_at': self.note.updated_at.isoformat() if self.note.updated_at else None
            }
        
        if include_emotion and self.emotion:
            result['emotion'] = {
                'id_emotion': self.emotion.id_emotion,
                'tipe_emosi': self.emotion.tipe_emosi
            }
        
        return result