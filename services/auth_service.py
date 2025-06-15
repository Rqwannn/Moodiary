from datetime import datetime, timedelta
from litestar.exceptions import HTTPException
from litestar.status_codes import (
    HTTP_400_BAD_REQUEST, 
    HTTP_401_UNAUTHORIZED, 
    HTTP_423_LOCKED, 
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND
)

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.Models.user import User, UserCreate, UserLogin, Token
from utils.security import security_manager
from typing import Optional
from uuid import UUID
from app.Database.config import Config
from utils.schema import UpdateUserData, GetUserData

import re

class AuthService:
    
    def _validate_email(self, email: str) -> bool:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    async def register_user(self, user_data: UserCreate, session: AsyncSession) -> User:
        if user_data.password != user_data.confirm_password:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Passwords do not match"
            )
        
        if not self._validate_email(user_data.email):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        if not security_manager.validate_password_strength(user_data.password):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character"
            )
        
        existing_user = await self._get_user_by_email(user_data.email, session)

        if existing_user:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_password = security_manager.get_password_hash(user_data.password)
        
        db_user = User(
            nama=user_data.nama,
            email=user_data.email,
            password=hashed_password, 
            tipe_keperibadian=user_data.tipe_keperibadian,
            is_active=True,
            is_verified=False
        )
        
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        
        return db_user
    
    async def authenticate_user(self, login_data: UserLogin, session: AsyncSession) -> Token:
        user = None

        if self._validate_email(login_data.credential):
            user = await self._get_user_by_email(login_data.credential, session)
        
        if not user:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if user.locked_until and user.locked_until > datetime.now():
            raise HTTPException(
                status_code=HTTP_423_LOCKED,
                detail=f"Account locked until {user.locked_until}"
            )
        
        if not security_manager.verify_password(login_data.password, user.password):
            user.failed_login_attempts += 1
            
            if user.failed_login_attempts >= Config.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.now() + timedelta(
                    minutes=Config.ACCOUNT_LOCKOUT_DURATION_MINUTES
                )
            
            await session.commit()
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Account deactivated"
            )
        
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now()
        user.updated_at = datetime.now()
        await session.commit()
        
        access_token = security_manager.create_access_token(
            data={"sub": user.email, "user_id": str(user.uid)}
        )
        refresh_token = security_manager.create_refresh_token(
            data={"sub": user.email, "user_id": str(user.uid)}
        )
        
        return Token(
            uid=user.uid,
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    async def refresh_token(self, refresh_token: str, session: AsyncSession) -> Token:
        token_data = security_manager.verify_token(refresh_token, "refresh")
        
        user = await self._get_user_by_email(token_data.email, session)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        access_token = security_manager.create_access_token(
            data={"sub": user.email, "user_id": str(user.uid)}
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def get_user_by_uid(self,
        data: str,
        session: AsyncSession) -> User:
        result = await session.exec(select(User).where(User.email == data))
        user = result.first()
        return user
    
    async def update_user_by_uid(
        self,
        uid: UUID,
        data: UpdateUserData,
        session: AsyncSession
    ) -> User:
        result = await session.exec(select(User).where(User.uid == uid))
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if data.email:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data.email):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
            email_check = await session.exec(
                select(User).where(User.email == data.email, User.uid != uid)
            )
            if email_check.first():
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
            user.email = data.email

        if data.password:
            if not security_manager.validate_password_strength(data.password):
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Password must be strong (min 8 chars, upper/lowercase, digit, symbol)"
                )
            user.password = security_manager.get_password_hash(data.password)

        if data.nama is not None:
            user.nama = data.nama
        
        if data.tipe_keperibadian is not None:
            user.tipe_keperibadian = data.tipe_keperibadian

        await session.commit()
        await session.refresh(user)

        return user
    
    async def get_current_user(self, token: str, session: AsyncSession) -> User:
        token_data = security_manager.verify_token(token)
        
        user = await self._get_user_by_email(token_data.email, session)
        if not user:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    async def _get_user_by_email(self, email: str, session: AsyncSession) -> Optional[User]:
        result = await session.exec(select(User).where(User.email == email))
        return result.first()
    
    async def _get_user_by_uid(self, uid: UUID, session: AsyncSession) -> Optional[User]:
        result = await session.exec(select(User).where(User.uid == uid))
        return result.first()

auth_service = AuthService()