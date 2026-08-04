from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.repositories.chat_repo import ChatRepository
from backend.app.workflows.business_assistant import MultiAgentOrchestrator
from backend.app.schemas.chat import ChatMessageCreate, ChatExecutionResult
from backend.app.models.user import User

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ChatRepository(db)

    def interact(self, request_data: ChatMessageCreate, user: User) -> ChatExecutionResult:
        session_id = request_data.session_id or "default_session"
        
        # 1. Save user input message to database
        self.repo.add_message(
            session_id=session_id,
            user_id=user.id,
            sender="user",
            content=request_data.message
        )

        # 2. Invoke LangGraph multi-agent supervisor pipeline
        execution_output = MultiAgentOrchestrator.execute(user_input=request_data.message)
        content = execution_output.get("response", "Assistant task completed.")
        agent_triggered = execution_output.get("agent_triggered", "Supervisor Agent")

        # 3. Save assistant response to database
        self.repo.add_message(
            session_id=session_id,
            user_id=user.id,
            sender=agent_triggered,
            content=content,
            model_used="openrouter/langgraph-orchestration"
        )

        return ChatExecutionResult(
            session_id=session_id,
            response=content,
            model_used="openrouter/langgraph-orchestration",
            agent_triggered=agent_triggered
        )
