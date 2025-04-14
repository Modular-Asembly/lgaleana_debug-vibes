from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.authentication import authenticate_user

router = APIRouter(prefix="/conversations", tags=["conversations"])

class CreateConversationRequest(BaseModel):
    user_id: int
    github_repository: str

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    github_repository: str

    class Config:
        orm_mode = True

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user),
) -> ConversationResponse:
    # Validate that the user exists based on provided user_id
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {payload.user_id} not found",
        )

    # Create the new conversation record associated with the user
    conversation = Conversation(user_id=payload.user_id, github_repository=payload.github_repository)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation
