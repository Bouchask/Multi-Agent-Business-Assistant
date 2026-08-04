from typing import Dict, Any, Optional
from loguru import logger
from backend.app.domain.scheduling.models import WorkingMemory, MissionProfile, AuditDecision, ExecutionResult, VerificationResult

class SchedulingMemoryManager:
    """
    Manages structured working memory for autonomous agent orchestration,
    avoiding bloated raw conversation replay and preventing state leakage across requests.
    """
    def __init__(self):
        self._store: Dict[str, WorkingMemory] = {}

    def get_session_memory(self, session_id: str = "default_session") -> WorkingMemory:
        if session_id not in self._store:
            self._store[session_id] = WorkingMemory(session_id=session_id)
        return self._store[session_id]

    def update_mission(self, mission: MissionProfile, session_id: str = "default_session"):
        mem = self.get_session_memory(session_id)
        mem.current_mission = mission
        mem.pending_tasks.append(f"Execute mission: {mission.mission.value} for '{mission.entities.title}'")

    def record_audit(self, decision: AuditDecision, session_id: str = "default_session"):
        mem = self.get_session_memory(session_id)
        mem.audit_decision = decision
        mem.previous_decisions.append(f"Audit decision: {decision.decision.value} (Confidence: {decision.confidence})")
        if decision.conversational_message:
            mem.open_questions.append(decision.conversational_message)

    def record_execution(self, execution: ExecutionResult, session_id: str = "default_session"):
        mem = self.get_session_memory(session_id)
        mem.execution_result = execution
        if execution.success:
            mem.completed_tasks.append(f"Executed tool action: {execution.action_attempted}")
            if f"Execute mission: {mem.current_mission.mission.value} for '{mem.current_mission.entities.title}'" in mem.pending_tasks:
                mem.pending_tasks.remove(f"Execute mission: {mem.current_mission.mission.value} for '{mem.current_mission.entities.title}'")
        else:
            mem.constraints.append(f"Execution errors encountered: {', '.join(execution.errors)}")

    def record_verification(self, verification: VerificationResult, session_id: str = "default_session"):
        mem = self.get_session_memory(session_id)
        mem.verification_result = verification
        mem.previous_decisions.append(f"Independent Verification Status: {verification.status.value}")

    def clear_session(self, session_id: str = "default_session"):
        self._store[session_id] = WorkingMemory(session_id=session_id)

memory_manager = SchedulingMemoryManager()
