import os
from typing import Any, Dict

import requests
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User

# A simple in-memory cache to store GitHub API responses
_auth_cache: Dict[str, Dict[str, Any]] = {}

# Initialize the security scheme
security = HTTPBearer(
    scheme_name="Authorization",
    description="Enter your Bearer token"
)

def fetch_github_user(token: str) -> Dict[str, Any]:
    """
    Calls the GitHub API to fetch public user data using the provided access token.
    Caches the result to avoid unnecessary API calls.

    Args:
        token (str): GitHub access token.

    Returns:
        Dict[str, Any]: User data from GitHub.
    """
    if token in _auth_cache:
        return _auth_cache[token]

    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid GitHub token or unable to fetch user data",
        )
    user_data = response.json()

    # Cache the result
    _auth_cache[token] = user_data
    return user_data


def authenticate_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to authenticate a user using a GitHub access token.
    Uses HTTPBearer security scheme to extract the token, calls the GitHub API to get user data,
    and retrieves the corresponding User record from the database using the GitHub ID.
    
    Caching is used to minimize GitHub API calls for identical tokens.
    
    Args:
        credentials (HTTPAuthorizationCredentials): The bearer token credentials.
        db (Session): SQLAlchemy session dependency.
    
    Returns:
        User: The authenticated User.
    
    Raises:
        HTTPException: If token is missing, invalid, or user is not found in the database.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization credentials missing",
        )

    token = credentials.credentials
    github_user = fetch_github_user(token)

    # Extract GitHub ID from response
    github_id = str(github_user["id"])  # Convert to string since our model stores it as String
    if not github_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="GitHub ID not found in response",
        )

    # Retrieve the corresponding User record from the database using github_id
    user = db.query(User).filter(User.github_id == github_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in the system",
        )

    return user
