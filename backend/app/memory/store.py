from typing import Dict, Optional
from loguru import logger
from backend.app.models.memory import WorkingMemoryModel
from backend.app.core.state import MissionState

class WorkingMemoryManager:
    """
    Enterprise Structured Working Memory Store.
    Replaces noisy conversation histories with concise, domain-relevant memory objects.
    Ensures every specialized agent receives only relevant state, tasks, and constraints.
    """
    def __init__(self):
        self._store: Dict[str, WorkingMemoryModel] = {}

    def get_memory(self, session_id: str = "default_session") -> WorkingMemoryModel:
        if session_id not in self._store:
            logger.debug(f"🧠 Initializing structured working memory for session '{session_id}'")
            self._store[session_id] = WorkingMemoryModel(session_id=session_id)
        return self._store[session_id]

    def reset_session(self, session_id: str = "default_session"):
        self._store[session_id] = WorkingMemoryModel(session_id=session_id)

    def update_status(self, new_state: MissionState, session_id: str = "default_session"):
        mem = self.get_memory(session_id)
        mem.execution_status = new_state

    def record_decision(self, decision: str, session_id: str = "default_session"):
        mem = self.get_memory(session_id)
        mem.previous_decisions.append(decision)

memory_manager = WorkingMemoryManager()
