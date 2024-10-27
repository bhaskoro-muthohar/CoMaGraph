from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from ..core.constants import ThreadStatus

class ThreadCreate(BaseModel):
    metadata: Optional[Dict] = Field(default_factory=dict)

class Thread(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: str = Field(default=ThreadStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict = Field(default_factory=dict)

class ThreadSummary(BaseModel):
    id: UUID
    message_count: int
    last_message_at: datetime
    topics: List[str]
    summary: str