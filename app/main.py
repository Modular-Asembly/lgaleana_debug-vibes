from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.db import engine, Base
from app.routes.user import router as user_router
from app.routes.conversation_get_or_create import router as conversation_router
from app.routes.message import router as message_router
from app.routes.users_get_all import router as users_all_router

def create_app() -> FastAPI:
    app = FastAPI()

    # Set up CORS middleware with hardcoded configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup HTTPBearer security scheme for Swagger UI
    app.dependency_overrides[HTTPBearer] = lambda: HTTPBearer(
        scheme_name="Authorization",
        description="Enter your Bearer token"
    )

    # Include routers
    app.include_router(user_router)
    app.include_router(conversation_router)
    app.include_router(message_router)
    app.include_router(users_all_router)

    # Create database tables
    Base.metadata.create_all(bind=engine)

    return app

app = create_app()
