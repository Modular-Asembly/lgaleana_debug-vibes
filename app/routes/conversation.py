from fastapi import APIRouter, HTTPException, status
from typing import Dict

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_or_get_conversation(payload: Dict) -> Dict:
    """
    Dummy implementation for the 'Get or Create Conversation' endpoint.
    It receives a JSON payload containing the 'github_repository', and returns a
    conversation with an empty list of messages.
    """
    # In a real implementation, you would validate the payload, check for an
    # existing conversation, create one if necessary, and return the conversation's messages.
    github_repository = payload.get("github_repository")
    if not github_repository:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'github_repository' in payload",
        )
    conversation = {
        "conversation_id": 1,
        "github_repository": github_repository,
        "messages": []
    }
    return conversation

@router.get("/{conversation_id}", status_code=status.HTTP_200_OK)
def get_conversation(conversation_id: int) -> Dict:
    """
    Dummy implementation to retrieve a conversation's details.
    """
    # In a real implementation, you would query the database.
    return {
        "conversation_id": conversation_id,
        "github_repository": "dummy-repository",
        "messages": []
    }
