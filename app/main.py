from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, Base
from app.routes.user import router as user_router
from app.routes.conversation import router as conversation_router
from app.routes.message import router as message_router

def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(user_router)
    app.include_router(conversation_router)
    app.include_router(message_router)
    
    Base.metadata.create_all(bind=engine)
    return app

app = create_app()
