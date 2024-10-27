from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from ...models.thread import Thread, ThreadCreate, ThreadSummary
from ...models.message import Message  # Add this import
from ...services.thread_service import ThreadService
from ...services.message_service import MessageService  # Add this import
from ...core.exceptions import ContextManagerException

router = APIRouter(prefix="/threads", tags=["threads"])

@router.post("/", response_model=Thread)
async def create_thread(
    thread: ThreadCreate,
    thread_service: ThreadService = Depends()
) -> Thread:
    """Create a new conversation thread"""
    try:
        return await thread_service.create_thread(thread)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{thread_id}/context", response_model=List[Message])
async def get_thread_context(
    thread_id: UUID,
    message_id: Optional[UUID] = None,
    window_size: Optional[int] = Query(default=None, le=50),
    message_service: MessageService = Depends()
) -> List[Message]:
    """Get context from a thread, optionally around a specific message"""
    try:
        return await message_service.get_thread_context(
            thread_id,
            message_id,
            window_size
        )
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{thread_id}", response_model=Thread)
async def get_thread(
    thread_id: UUID,
    thread_service: ThreadService = Depends()
) -> Thread:
    """Get thread details"""
    try:
        return await thread_service.get_thread(thread_id)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{thread_id}/summary", response_model=ThreadSummary)
async def get_thread_summary(
    thread_id: UUID,
    thread_service: ThreadService = Depends()
) -> ThreadSummary:
    """Get thread summary with topics and analytics"""
    try:
        return await thread_service.get_thread_summary(thread_id)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))

# src/api/routes/messages.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
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