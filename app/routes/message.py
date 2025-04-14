from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Dict

from app.db import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.authentication import authenticate_user

router = APIRouter(prefix="/messages", tags=["messages"])

class AddMessageRequest(BaseModel):
    conversation_id: int = Field(..., description="ID of the conversation")
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    conversation_id: int

    class Config:
        orm_mode = True

@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_message(
    payload: AddMessageRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(authenticate_user)
) -> MessageResponse:
    # Validate that the conversation exists
    conversation = db.query(Conversation).filter(Conversation.id == payload.conversation_id).first()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with id {payload.conversation_id} not found",
        )
    
    # Create new Message record
    new_message = Message(
        role=payload.role,
        content=payload.content,
        conversation_id=payload.conversation_id
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message
