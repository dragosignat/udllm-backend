from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.sql import func
from app.database.database import Base

class SystemPrompt(Base):
    __tablename__ = "SystemPrompts"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, unique=True)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    used = Column(Integer, default=0)