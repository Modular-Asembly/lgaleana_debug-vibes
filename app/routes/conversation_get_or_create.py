from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.authentication import authenticate_user
from app.db import get_db
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter(prefix="/conversations", tags=["conversations"])

class MessageResponse(BaseModel):
    id: int = Field(..., description="Message identifier")
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")
    conversation_id: int = Field(..., description="Associated conversation ID")

    class Config:
        orm_mode = True

class ConversationResponse(BaseModel):
    id: int = Field(..., description="Conversation identifier")
    github_repository: str = Field(..., description="GitHub repository associated with the conversation")
    user_id: int = Field(..., description="ID of the user owning this conversation")
    messages: List[MessageResponse] = Field(default_factory=list, description="List of messages in the conversation")

    class Config:
        orm_mode = True

@router.get("/", response_model=ConversationResponse, status_code=status.HTTP_200_OK)
def get_or_create_conversation(
    github_repository: str = Query(..., description="GitHub repository identifier"),
    db: Session = Depends(get_db),
    current_user = Depends(authenticate_user),
) -> ConversationResponse:
    """
    Get or create a conversation based on the provided GitHub repository.
    Authenticates the user via the authentication module. Then, it looks for a conversation record
    that belongs to the authenticated user and matches the given GitHub repository. If it doesn't exist,
    a new conversation is created. Regardless, it returns the conversation along with all its associated messages.
    """
    # Look for an existing conversation for current user and given repository.
    conversation: Conversation | None = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .filter(Conversation.github_repository == github_repository)
        .first()
    )

    if not conversation:
        # Create new conversation record with no messages.
        conversation = Conversation(
            github_repository=github_repository,
            user_id=current_user.id
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Load associated messages (relationship should be lazy loaded)
    messages = conversation.messages

    return ConversationResponse(
        id=conversation.id,
        github_repository=conversation.github_repository,
        user_id=conversation.user_id,
        messages=messages
    )
