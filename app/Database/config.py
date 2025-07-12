import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://postgres:admin@localhost:5433/moodiary" # Local Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-this")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3

    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 30
    
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_MINUTES: int = 15

async_engine = create_async_engine(url=Config.SQLALCHEMY_DATABASE_URI, echo=True)