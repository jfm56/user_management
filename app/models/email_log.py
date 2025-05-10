from sqlalchemy import Column, String, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class EmailLog(Base):
    __tablename__ = 'email_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    email_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    recipient = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text, nullable=True)
