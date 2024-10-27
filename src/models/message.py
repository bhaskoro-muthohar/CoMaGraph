from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
from datetime import datetime
from uuid import UUID, uuid4
from ..core.constants import MessageRole

class MessageCreate(BaseModel):
    content: str
    role: str = Field(..., pattern="^(user|assistant)$")
    thread_id: UUID
    metadata: Optional[Dict] = Field(default_factory=dict)

class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(default_factory=uuid4)
    content: str
    role: str
    thread_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    embedding: Optional[List[float]] = None
    metadata: Dict = Field(default_factory=dict)