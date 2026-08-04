from typing import List
from sqlalchemy.orm import Session
from backend.app.models.chat_history import ChatHistory

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_message(self, session_id: str, user_id: int, sender: str, content: str, model_used: str = None) -> ChatHistory:
        msg = ChatHistory(
            session_id=session_id,
            user_id=user_id,
            sender=sender,
            content=content,
            model_used=model_used
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_session_messages(self, session_id: str, user_id: int, limit: int = 50) -> List[ChatHistory]:
        return self.db.query(ChatHistory)\
            .filter(ChatHistory.session_id == session_id, ChatHistory.user_id == user_id)\
            .order_by(ChatHistory.created_at.asc())\
            .limit(limit).all()
