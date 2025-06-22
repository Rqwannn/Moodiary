from litestar import Controller, get, post, put, delete
from litestar.exceptions import NotFoundException, ValidationException
from litestar.status_codes import HTTP_201_CREATED, HTTP_200_OK
from litestar.params import Body, Parameter

from typing import List, Optional
from sqlalchemy import select, update, delete as sql_delete
from sqlalchemy.orm import selectinload

from app.Models.notes import Notes
from app.DTOs.notes_dto import NotesCreateDTO, NotesUpdateDTO, NotesResponseDTO
from app.Database.connection import get_session
from datetime import datetime

from app.Models.user import User

from uuid import UUID

class NotesController(Controller):
    path = "/api"
    tags = ["Notes"]

    @post("/notes/create", status_code=HTTP_201_CREATED)
    async def create_note(
        self, 
        data: NotesCreateDTO,
    ) -> NotesResponseDTO:
        
        async with get_session() as db_session:

            try:
                # Verify user exists (optional validation)
                user_query = select(User).where(User.uid == data.id_user)
                user_result = await db_session.exec(user_query)
                if not user_result.first():
                    raise ValidationException("User not found")

                # Create new note
                new_note = Notes(
                    title=data.title,
                    content=data.content,
                    id_user=data.id_user
                )
                
                db_session.add(new_note)
                await db_session.commit()
                await db_session.refresh(new_note)
                
                return NotesResponseDTO.from_orm(new_note)
                
            except Exception as e:
                await db_session.rollback()
                raise ValidationException(f"Failed to create note: {str(e)}")

    @get("/notes/get_all")
    async def get_all_notes(
        self,
        user_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[NotesResponseDTO]:
        
        async with get_session() as db_session:

            query = select(Notes).options(selectinload(Notes.user))
            
            if user_id:
                query = query.where(Notes.id_user == user_id)
                
            query = query.limit(limit).offset(offset).order_by(Notes.created_at.desc())
            
            result = await db_session.exec(query)
            notes = result.scalars().all()
            
            return [NotesResponseDTO.from_orm(note) for note in notes]

    @get("/notes/get_single/{note_id:int}")
    async def get_note_by_id(
        self, 
        note_id: int,
    ) -> NotesResponseDTO:
        
        async with get_session() as db_session:

            query = select(Notes).options(
                selectinload(Notes.user),
                selectinload(Notes.note_emotions)
            ).where(Notes.id_notes == note_id)
            
            result = await db_session.exec(query)
            note = result.scalars().first()
            
            if not note:
                raise NotFoundException(f"Note with ID {note_id} not found")
                
            return NotesResponseDTO.from_orm(note)

    @put("/notes/update/{note_id:int}")
    async def update_note(
        self,
        note_id: int,
        data: NotesUpdateDTO,
    ) -> NotesResponseDTO:

        async with get_session() as db_session:
            # Cek apakah note ada
            query = select(Notes).where(Notes.id_notes == note_id)
            result = await db_session.exec(query)
            note = result.scalars().first()

            if not note:
                raise NotFoundException(f"Note with ID {note_id} not found")

            # Update fields
            update_data = data.model_dump(exclude_unset=True, exclude_none=True)
            if update_data:
                update_data['updated_at'] = datetime.now()
                stmt = (
                    update(Notes)
                    .where(Notes.id_notes == note_id)
                    .values(**update_data)
                )
                await db_session.exec(stmt)
                await db_session.commit()

                # Ambil ulang dari DB sebagai ORM instance
                updated_note = await db_session.get(Notes, note_id)
                if not updated_note:
                    raise NotFoundException(detail="Updated note not found")

                return NotesResponseDTO.from_orm(updated_note)

            return NotesResponseDTO.from_orm(note)


    @delete("/notes/delete/{note_id:int}", status_code=HTTP_200_OK)
    async def delete_note(
        self,
        note_id: int,
    ) -> None:
        
        async with get_session() as db_session:

            # Check if note exists
            query = select(Notes).where(Notes.id_notes == note_id)
            result = await db_session.exec(query)
            note = result.first()
            
            if not note:
                raise NotFoundException(f"Note with ID {note_id} not found")
            
            # Delete the note
            stmt = sql_delete(Notes).where(Notes.id_notes == note_id)
            await db_session.exec(stmt)
            await db_session.commit()

            return {
                "message": f"Data dengan ID Notes {note_id} berhasil di hapus"
            }

    @get("/notes/search")
    async def search_notes(
        self,
        q: str = None, # title or content
        user_id: Optional[UUID] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[NotesResponseDTO]:
        
        async with get_session() as db_session:

            if not q or len(q.strip()) < 2:
                raise ValidationException("Search query must be at least 2 characters")
            
            search_term = f"%{q.strip()}%"
            query = select(Notes).options(selectinload(Notes.user)).where(
                (Notes.title.ilike(search_term)) | (Notes.content.ilike(search_term))
            )
            
            if user_id:
                query = query.where(Notes.id_user == user_id)
                
            query = query.limit(limit).offset(offset).order_by(Notes.updated_at.desc())
            
            result = await db_session.exec(query)
            notes = result.scalars().all()
            
            return [NotesResponseDTO.from_orm(note) for note in notes]