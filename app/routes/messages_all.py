from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.authentication import authenticate_user

router = APIRouter(prefix="/messages", tags=["messages"])

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    conversation_id: int

    class Config:
        orm_mode = True

@router.get("/all", response_model=List[MessageResponse], status_code=status.HTTP_200_OK)
def get_all_messages(
    github_repository: str = Query(..., description="GitHub repository to filter conversations"),
    db: Session = Depends(get_db),
    current_user = Depends(authenticate_user)
) -> List[MessageResponse]:
    # Retrieve conversations filtered by the provided GitHub repository
    conversations = db.query(Conversation).filter(Conversation.github_repository == github_repository).all()
    if not conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No conversations found for the specified repository"
        )
    
    conversation_ids = [conversation.id for conversation in conversations]
    # Retrieve all messages that belong to the filtered conversations
    messages = db.query(Message).filter(Message.conversation_id.in_(conversation_ids)).all()
    return messages
