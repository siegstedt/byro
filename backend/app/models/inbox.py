from sqlalchemy import Column, String, Enum, JSON, UUID, DateTime
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class InboxItem(Base):
    __tablename__ = "inbox_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(Enum("processing", "review", "done", "error", name="inbox_status"), default="processing")
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    ai_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())