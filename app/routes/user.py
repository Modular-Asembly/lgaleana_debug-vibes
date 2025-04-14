from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.authentication import authenticate_user
from typing import Any, Dict

router = APIRouter(prefix="/users", tags=["users"])

class CreateOrGetUserRequest(BaseModel):
    id: str = Field(..., description="GitHub ID")
    login: str = Field(..., description="GitHub username")
    email: str = Field(..., description="Email address")

    class Config:
        extra = "allow"  # Allow extra fields to be stored

class UserResponse(BaseModel):
    id: int
    github_id: str
    email: str
    raw_data: Dict[str, Any]

    class Config:
        orm_mode = True

@router.post("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
def create_or_get_user(
    payload: CreateOrGetUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user)
) -> UserResponse:
    # Check if a user with the given GitHub ID already exists.
    existing_user: User | None = db.query(User).filter(User.github_id == payload.id).first()
    if existing_user:
        return existing_user

    # Create a new user record with the entire payload as raw_data.
    raw_payload: Dict[str, Any] = payload.dict(by_alias=True, exclude_unset=False)
    new_user = User(
        github_id=payload.id,
        email=payload.email,
        raw_data=raw_payload
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
