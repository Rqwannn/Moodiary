import os
from typing import AsyncGenerator

from sqlmodel import text, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from app.Database.config import async_engine

async_session = sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db():
    async with async_engine.begin() as conn:
        from app.Models.user import User
        from app.Models.notes import Note

        await conn.run_sync(SQLModel.metadata.create_all)

@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

def execute_query(query: str, params: tuple = ()) -> list:
    """Execute a SELECT query and return results."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an INSERT, UPDATE, or DELETE query and return affected rows."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount

def execute_insert(query: str, params: tuple = ()) -> int:
    """Execute an INSERT query and return the last row ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    
@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide the session object"""
    async_session = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()