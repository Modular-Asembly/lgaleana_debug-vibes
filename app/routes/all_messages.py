from fastapi import APIRouter, HTTPException, status
from typing import Dict, List

router = APIRouter(prefix="/all-messages", tags=["all-messages"])

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_messages() -> Dict[str, List]:
    """
    Dummy implementation for retrieving all messages from all conversations.
    """
    # In a real application, you would query the database for all messages.
    return {
        "messages": []
    }
