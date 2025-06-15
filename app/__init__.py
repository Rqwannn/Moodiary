from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig

from huggingface_hub import login
from routes.routes import routes
from app.Database.connection import init_db
import os

async def startup_handler() -> None:
    await init_db()

def create_app() -> Litestar:    
    cors_config = CORSConfig(
        allow_origins=["*"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    openapi_config = OpenAPIConfig(
        title="Moodiary API",
        version="1.0.0",
        description="A Project For Moodiary",
    )
    
    app = Litestar(
        route_handlers=routes,
        cors_config=cors_config,
        openapi_config=openapi_config,
        on_startup=[startup_handler],  # Initialize database on startup
        debug=True
    )

    login(token=os.getenv("HUGGINGFACE_API_KEY"))
    
    return app

apps = create_app()