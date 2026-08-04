from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.core.state import MissionState
from backend.app.models.base import StructuredMission, TaskDefinition, ToolExecutionResult, VerificationReport

class WorkingMemoryModel(BaseModel):
    session_id: str = "default_session"
    active_mission: Optional[StructuredMission] = None
    current_objective: str = "Await executive directives."
    completed_tasks: List[TaskDefinition] = Field(default_factory=list)
    pending_tasks: List[TaskDefinition] = Field(default_factory=list)
    tool_results: List[ToolExecutionResult] = Field(default_factory=list)
    verifications: List[VerificationReport] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    previous_decisions: List[str] = Field(default_factory=list)
    execution_status: MissionState = Field(default=MissionState.NEW)
    confidence: float = 1.0
    open_questions: List[str] = Field(default_factory=list)

    def summarize_context(self) -> str:
        completed = [t.task_name for t in self.completed_tasks]
        pending = [t.task_name for t in self.pending_tasks]
        return (
            f"Objective: {self.current_objective}\n"
            f"Status: {self.execution_status.value} | Confidence: {self.confidence}\n"
            f"Completed Tasks: {', '.join(completed) if completed else 'None'}\n"
            f"Pending Tasks: {', '.join(pending) if pending else 'None'}\n"
            f"Constraints & Open Questions: {'; '.join(self.constraints + self.open_questions)}"
        )
