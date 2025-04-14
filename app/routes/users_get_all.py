from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.authentication import authenticate_user
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

class UserResponse(BaseModel):
    id: int
    github_id: str
    email: str
    raw_data: dict

    class Config:
        orm_mode = True

@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all users",
    description="Retrieve all user records from the database. Requires authentication."
)
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user)
) -> List[UserResponse]:
    users: List[User] = db.query(User).all()
    return users
