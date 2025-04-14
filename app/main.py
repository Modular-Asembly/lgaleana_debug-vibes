from dotenv import load_dotenv
load_dotenv()  # Must be called immediately before any other imports to load environment variables

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.db import engine, Base
from app.routes.user import router as user_router
from app.routes.conversation_get_or_create import router as conversation_router
from app.routes.message import router as message_router

# Use the message_router again as messages_all_router per requirements.
messages_all_router = message_router

def create_app() -> FastAPI:
    """Initialize and configure the FastAPI application."""
    app = FastAPI()

    # Setup CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup a security scheme for Swagger UI
    security_scheme = HTTPBearer(
        scheme_name="Authorization",
        description="Enter your Bearer token"
    )
    # Set the schemes in the OpenAPI schema manually
    if not app.openapi_schema:
        # Store the original openapi method
        original_openapi = app.openapi

        def custom_openapi() -> dict:
            if app.openapi_schema:
                return app.openapi_schema
            openapi_schema = original_openapi()
            openapi_schema["components"]["securitySchemes"] = {
                "HTTPBearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Enter your Bearer token"
                }
            }
            # Apply the security scheme globally; individual endpoints can override if necessary.
            openapi_schema["security"] = [{"HTTPBearer": []}]
            app.openapi_schema = openapi_schema
            return app.openapi_schema
        app.openapi = custom_openapi

    # Include routers
    app.include_router(user_router)
    app.include_router(conversation_router)
    app.include_router(message_router)
    app.include_router(messages_all_router)

    # Initialize the database by creating all tables defined in the models.
    Base.metadata.create_all(bind=engine)
    
    return app

app = create_app()
