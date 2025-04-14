from dotenv import load_dotenv
load_dotenv()  # Load environment variables early

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from app.routes.user import router as user_router
from app.routes.conversation import router as conversation_router
from app.routes.message import router as message_router
from app.routes.messages_all import router as messages_all_router
from app.db import Base, engine

def create_app() -> FastAPI:
    app = FastAPI()

    # Setup CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup security scheme for Swagger UI
    security = HTTPBearer(
        scheme_name="Authorization",
        description="Enter your Bearer token"
    )

    # Include API routers
    app.include_router(user_router)
    app.include_router(conversation_router)
    app.include_router(message_router)
    app.include_router(messages_all_router)

    # Create database tables
    Base.metadata.create_all(bind=engine)

    return app

app = create_app()
