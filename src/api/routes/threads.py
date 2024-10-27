from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID
from ...models.thread import Thread, ThreadCreate, ThreadSummary
from ...models.message import Message
from ...services.thread_service import ThreadService
from ...services.message_service import MessageService
from ...core.exceptions import ContextManagerException
from ..deps import get_thread_service, get_message_service

router = APIRouter(prefix="/threads", tags=["threads"])

@router.post("/", response_model=Thread, operation_id="create_new_thread")
async def create_thread(
    thread: ThreadCreate,
    thread_service: ThreadService = Depends(get_thread_service)
) -> Thread:
    """Create a new conversation thread"""
    try:
        return await thread_service.create_thread(thread)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{thread_id}/context", response_model=List[Message], operation_id="get_thread_context")
async def get_thread_context(
    thread_id: UUID,
    message_id: Optional[UUID] = None,
    window_size: Optional[int] = Query(default=None, le=50),
    message_service: MessageService = Depends(get_message_service)
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

@router.get("/{thread_id}", response_model=Thread, operation_id="get_thread_by_id")
async def get_thread(
    thread_id: UUID,
    thread_service: ThreadService = Depends(get_thread_service)
) -> Thread:
    """Get thread details"""
    try:
        return await thread_service.get_thread(thread_id)
    except ContextManagerException as e:
        raise HTTPException(status_code=400, detail=str(e))