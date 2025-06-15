from litestar import Controller, post, get, put
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_200_OK
from litestar.params import Body, Parameter
from litestar.di import Provide

from app.Database.connection import get_session
from app.Models.user import UserCreate, UserLogin, UserResponse, Token, User
from services.auth_service import auth_service

from utils.schema import UpdateUserData, RefreshTokenRequest

class Authentication(Controller):
    path = "/api"
    
    @post("/register")
    async def register(
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
    
    @post("/login")
    async def login(
        self,
        data: UserLogin = Body(),
    ) -> Token:
        async with get_session() as session:
            return await auth_service.authenticate_user(data, session)

    @put("/edit_profile", status_code=HTTP_200_OK)
    async def edit_users(
        self,
        data: UpdateUserData = Body(),
    ) -> User:
        async with get_session() as session:
            return await auth_service.update_user_by_uid(data.uid, data, session)

    @get("/get_profile/{email:str}", status_code=HTTP_200_OK)
    async def get_users(
        self,
        email: str = Parameter(),
    ) -> User:
        async with get_session() as session:
            return await auth_service.get_user_by_uid(email, session)

    @post("/refresh")
    async def refresh_token(
        self,
        data: RefreshTokenRequest = Body(),
    ) -> Token:
        async with get_session() as session:
            return await auth_service.refresh_token(data, session)