from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.Models.notes import Notes

from uuid import UUID

class NotesCreateDTO(BaseModel):
    """DTO for creating a new note"""
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    id_user: UUID = Field(..., description="User ID who owns the note")


class NotesUpdateDTO(BaseModel):
    """DTO for updating a note"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Note title")
    content: Optional[str] = Field(None, min_length=1, description="Note content")


class NotesResponseDTO(BaseModel):
    """DTO for note responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id_notes: int
    id_user: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_orm(cls, note: Notes) -> "NotesResponseDTO":
        return cls(
            id_notes=note.id_notes,
            id_user=note.id_user,
            title=note.title,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at
        )


class NotesWithUserDTO(NotesResponseDTO):
    """DTO for note responses with user information"""
    user_name: str
    user_email: str
    
    @classmethod
    def from_orm(cls, note: Notes) -> "NotesWithUserDTO":
        return cls(
            id_notes=note.id_notes,
            id_user=note.id_user,
            title=note.title,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at,
            user_name=note.user.nama if note.user else "Unknown",
            user_email=note.user.email if note.user else "Unknown"
        )