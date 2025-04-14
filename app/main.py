from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from app.db import engine, Base
from app.routes.user import router as user_router
from app.routes.message import router as message_router
from app.routes.conversation import router as conversation_router
from app.routes.all_messages import router as messages_all_router

app = FastAPI()

# Setup CORS middleware with hardcoded configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup security scheme for Swagger UI using FastAPI's HTTPBearer
security_scheme = HTTPBearer(
    scheme_name="Authorization",
    description="Enter your Bearer token"
)

# Include API routers
app.include_router(user_router)
app.include_router(message_router)
app.include_router(conversation_router)
app.include_router(messages_all_router)

# Create the database tables
Base.metadata.create_all(bind=engine)
