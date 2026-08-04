import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender = Column(String(50), nullable=False)  # "user", "assistant", or specialized agent name
    content = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    user = relationship("User")
