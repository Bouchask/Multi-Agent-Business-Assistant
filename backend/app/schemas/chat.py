from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ChatMessageCreate(BaseModel):
    session_id: Optional[str] = "default_session"
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    user_id: int
    sender: str
    content: str
    model_used: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatExecutionResult(BaseModel):
    session_id: str
    response: str
    model_used: Optional[str] = None
    agent_triggered: Optional[str] = "Supervisor Agent"
