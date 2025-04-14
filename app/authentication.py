import os
from typing import Any, Dict

import requests
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User

# A simple in-memory cache to store GitHub API responses
_auth_cache: Dict[str, Dict[str, Any]] = {}


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


def authenticate_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    FastAPI dependency to authenticate a user using a GitHub access token.
    Extracts the token from the 'Authorization' header, calls the GitHub API to get user data,
    and retrieves the corresponding User record from the database.
    
    Caching is used to minimize GitHub API calls for identical tokens.
    
    Args:
        request (Request): The incoming request.
        db (Session): SQLAlchemy session dependency.
    
    Returns:
        User: The authenticated User.
    
    Raises:
        HTTPException: If token is missing, invalid, or user is not found in the database.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    # Expecting header format: "token <access_token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
        )
    
    token = parts[1]
    github_user = fetch_github_user(token)

    # Extract email from GitHub data; if not provided directly, additional logic could be added
    email = github_user.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found in GitHub response",
        )

    # Retrieve the corresponding User record from the database
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in the system",
        )

    return user
