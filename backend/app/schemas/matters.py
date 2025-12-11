from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class MatterBase(BaseModel):
    title: str
    category: str
    attributes: Optional[dict] = None

class MatterCreate(MatterBase):
    pass

class MatterResponse(MatterBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True