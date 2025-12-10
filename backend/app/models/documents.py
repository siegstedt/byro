from sqlalchemy import Column, ForeignKey, String, UUID, Text, DateTime
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import uuid
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matter_id = Column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    title = Column(String, nullable=False)
    content_text = Column(Text, nullable=True)
    content_embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())