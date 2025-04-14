from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.authentication import authenticate_user
from typing import Any, Dict

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    id: int
    github_id: str
    email: str
    raw_data: Dict[str, Any]

    class Config:
        orm_mode = True


@router.post("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
def create_or_get_user(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
) -> UserResponse:
    # Check if a user with the given GitHub ID already exists.
    existing_user: User | None = (
        db.query(User).filter(User.github_id == payload["sub"]).first()
    )
    if existing_user:
        return existing_user

    # Create a new user record with the entire payload as raw_data.
    new_user = User(github_id=payload["sub"], email=payload["email"], raw_data=payload)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
