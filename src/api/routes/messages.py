from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from ...models.message import Message, MessageCreate
from ...services.message_service import MessageService
from ...core.exceptions import ContextManagerException

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=Message)
async def create_message(
    message: MessageCreate,
    message_service: MessageService = Depends()
) -> Message:
    """Create a new message in a thread"""
    try:
        return await message_service.create_message(message)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create message")

@router.get("/{message_id}", response_model=Message)
async def get_message(
    message_id: UUID,
    message_service: MessageService = Depends()
) -> Message:
    """Get a specific message by ID"""
    try:
        message = await message_service.get_message(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/similar/", response_model=List[Message])
async def find_similar_messages(
    content: str = Query(..., description="Content to find similar messages for"),
    limit: int = Query(default=5, le=20),
    message_service: MessageService = Depends()
) -> List[Message]:
    """Find messages similar to the provided content"""
    try:
        return await message_service.get_similar_messages(content, limit)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))