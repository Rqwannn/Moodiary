from litestar import Controller, post, get, put, delete
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_200_OK
from litestar.params import Body, Parameter
from litestar.di import Provide

from app.Database.connection import get_session
from app.Models.user import UserCreate, UserLogin, UserResponse, Token, User
from services.auth_service import auth_service

class Notes(Controller):
    path = "/api"
    
    @post("/notes/create")
    async def create(
        self,
        data: UserCreate = Body(),
    ) -> UserResponse:
        async with get_session() as session:

            user = await auth_service.register_user(data, session)

            return UserResponse(
                uid=user.uid,
                nama=user.nama,
                email=user.email,
                tipe_keperibadian=user.tipe_keperibadian,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                last_login=user.last_login
            )