from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.Models.notes import Note

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)
    nama: str = Field(index=True, max_length=50)
    tipe_keperibadian: str = Field(default=None, max_length=20)

class User(UserBase, table=True):
    __tablename__ = 'users'
    
    uid: UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True,
        unique=True, default=uuid4)
    )

    email: str = Field(unique=True, index=True, max_length=255)
    password: str = Field(max_length=255)
    nama: str = Field(default=None, max_length=50)
    tipe_keperibadian: str = Field(unique=True, index=True, max_length=20)
    
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    last_login: Optional[datetime] = Field(default=None)
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)
    
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    notes_list: List["Note"] = Relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User => {self.email}"

class UserCreate(SQLModel):
    email: str = Field(max_length=255)
    password: str = Field(max_length=100)
    confirm_password: str
    nama: str = Field(min_length=3, max_length=50)
    tipe_keperibadian: str = Field(default=None, max_length=20)

class UserLogin(SQLModel):
    credential: str  # Bisa login dengan nrp atau email
    password: str

class UserResponse(SQLModel):
    uid: UUID
    nama: str
    email: str
    tipe_keperibadian: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

class Token(SQLModel):
    uid: UUID
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(SQLModel):
    email: Optional[str] = None
    user_id: Optional[UUID] = None