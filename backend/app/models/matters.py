from sqlalchemy import Column, String, Enum, JSON, UUID, DateTime
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

class Matter(Base):
    __tablename__ = "matters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    attributes = Column(JSON, nullable=True)
    status = Column(Enum("active", "expired", "terminated", name="matter_status"), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())