from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class InboxItemBase(BaseModel):
    original_filename: str
    file_path: str
    status: str = "processing"

class InboxItemResponse(InboxItemBase):
    id: UUID
    ai_payload: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True