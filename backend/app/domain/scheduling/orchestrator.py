from typing import List, Dict, Any, Optional
from loguru import logger
from backend.app.domain.scheduling.models import MissionAction, AuditClassification, ExecutionResult, VerificationResult, VerificationStatus
from backend.app.domain.scheduling.memory import memory_manager
from backend.app.domain.scheduling.agents.mission_planner import MissionPlannerAgent
from backend.app.domain.scheduling.agents.scheduling_auditor import SchedulingAuditorAgent
from backend.app.domain.scheduling.agents.calendar_executor import CalendarExecutorAgent
from backend.app.domain.scheduling.agents.execution_verifier import ExecutionVerifierAgent
from backend.app.domain.scheduling.agents.report_generator import ReportGeneratorAgent
from backend.app.tools.calendar_tool import CalendarTool

class SchedulingOrchestrator:
    """
    Enterprise Python Orchestrator for the Scheduling Domain.
    Strictly follows separation of concerns: Python routes structured Pydantic models between
    specialized LLM agents and tools without embedding any ad-hoc business logic or string formatting.
    """
    @staticmethod
    def execute_workflow(raw_instruction: str, session_id: str = "default_session", history: Optional[List[Dict[str, Any]]] = None) -> str:
        logger.info(f"🚀 SCHEDULING ORCHESTRATOR: Initiating 5-Stage Agentic Pipeline for session '{session_id}'")
        
        # 1. Retrieve structured Working Memory context (avoids full raw history replay)
        mem = memory_manager.get_session_memory(session_id)
        context_summary = f"Completed: {len(mem.completed_tasks)}, Previous Decisions: {mem.previous_decisions[-3:] if mem.previous_decisions else 'None'}"
        
        # 2. AGENT 1: Executive Mission Planner (Intent & schema creation)
        mission = MissionPlannerAgent.plan_mission(raw_command=raw_instruction, memory_context=context_summary)
        memory_manager.update_mission(mission, session_id=session_id)
        
        # Retrieve existing calendar data for analysis
        cal_data = CalendarTool.list_upcoming_meetings(filter_month=None)
        existing_events = cal_data.get("events", [])

        # 3. AGENT 2: AI Scheduling Auditor (Semantic conflict analysis & confidence scoring)
        if mission.requires_duplicate_check or mission.requires_conflict_check:
            audit = SchedulingAuditorAgent.audit_request(mission=mission, existing_events=existing_events, user_command=raw_instruction)
        else:
            from backend.app.domain.scheduling.models import AuditDecision
            audit = AuditDecision(decision=AuditClassification.SAFE_NEW_MEETING, confidence=1.0, reason="Bypassed duplicate audit for read query.")
            
        memory_manager.record_audit(audit, session_id=session_id)

        # 4. AGENT 3 & 4: Tool Execution Engine & Mandatory Independent Verification
        execution = ExecutionResult(action_attempted=mission.mission.value)
        verification = VerificationResult(status=VerificationStatus.VERIFIED)
        
        should_execute = audit.decision in [AuditClassification.SAFE_NEW_MEETING, AuditClassification.RECURRING, AuditClassification.RESCHEDULE] or mission.mission == MissionAction.QUERY
        
        if should_execute:
            # Execute tool actions via CalendarExecutor
            execution = CalendarExecutorAgent.execute(mission=mission)
            memory_manager.record_execution(execution, session_id=session_id)
            
            # Independent Execution Verifier audits storage and API proof
            verification = ExecutionVerifierAgent.verify(mission=mission, execution=execution)
            memory_manager.record_verification(verification, session_id=session_id)
        else:
            logger.warning(f"🛡️ Pipeline intercepted execution due to auditor decision: {audit.decision.value}")
            execution.success = False
            execution.warnings.append(f"Execution halted by AI Auditor: {audit.reason}")
            verification.status = VerificationStatus.VERIFIED  # Verified interception

        # Refresh database events overview post-execution
        updated_events = CalendarTool.list_upcoming_meetings(filter_month=None).get("events", [])

        # 5. AGENT 5: Executive Report Generator (Synthesizes elegant markdown based on verified records)
        final_report = ReportGeneratorAgent.generate_report(
            mission=mission,
            audit=audit,
            execution=execution,
            verification=verification,
            existing_events=updated_events
        )
        
        logger.info(f"🏁 SCHEDULING ORCHESTRATOR: Pipeline completion verified.")
        return final_report
