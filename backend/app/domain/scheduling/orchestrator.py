from typing import List, Dict, Any, Optional
from loguru import logger
from backend.app.domain.scheduling.models import MissionAction, AuditClassification, ExecutiveRiskLevel, ExecutionResult, VerificationResult, VerificationStatus
from backend.app.domain.scheduling.memory import memory_manager
from backend.app.domain.scheduling.agents.mission_planner import MissionPlannerAgent
from backend.app.domain.scheduling.agents.scheduling_auditor import SchedulingAuditorAgent
from backend.app.domain.scheduling.agents.calendar_executor import CalendarExecutorAgent
from backend.app.domain.scheduling.agents.execution_verifier import ExecutionVerifierAgent
from backend.app.domain.scheduling.agents.report_generator import ReportGeneratorAgent
from backend.app.tools.calendar_tool import CalendarTool

class SchedulingOrchestrator:
    """
    Enterprise Python Orchestrator for the AI Executive Operating System.
    Strictly follows separation of concerns: Python routes structured Pydantic models between
    specialized LLM agents and tools without embedding any ad-hoc business logic or string formatting.
    """
    @staticmethod
    def execute_workflow(raw_instruction: str, session_id: str = "default_session", history: Optional[List[Dict[str, Any]]] = None) -> str:
        logger.info(f"🚀 SCHEDULING ORCHESTRATOR: Initiating Autonomous Executive Pipeline for session '{session_id}'")
        
        # 1. Retrieve structured Working Memory context (avoids full raw history replay)
        mem = memory_manager.get_session_memory(session_id)
        context_summary = f"Completed: {len(mem.completed_tasks)}, Previous Decisions: {mem.previous_decisions[-3:] if mem.previous_decisions else 'None'}"
        
        # 2. AGENT 1: Executive Mission Planner (Intent & schema creation)
        mission = MissionPlannerAgent.plan_mission(raw_command=raw_instruction, memory_context=context_summary)
        memory_manager.update_mission(mission, session_id=session_id)
        
        # Retrieve existing calendar data for analysis
        cal_data = CalendarTool.list_upcoming_meetings(filter_month=None)
        existing_events = cal_data.get("events", [])

        # 3. AGENT 2: AI Scheduling Auditor & Risk Evaluator
        if mission.requires_duplicate_check or mission.requires_conflict_check or mission.mission in [MissionAction.DELETE, MissionAction.CANCEL]:
            audit = SchedulingAuditorAgent.audit_request(mission=mission, existing_events=existing_events, user_command=raw_instruction)
        else:
            from backend.app.domain.scheduling.models import AuditDecision
            audit = AuditDecision(decision=AuditClassification.SAFE_NEW_MEETING, risk_level=ExecutiveRiskLevel.ROUTINE_SAFE, confidence=1.0, reason="Bypassed duplicate audit for routine read query.")
            
        memory_manager.record_audit(audit, session_id=session_id)

        # 4. AGENT 3 & 4: Tool Execution Engine & Mandatory Independent Verification
        execution = ExecutionResult(action_attempted=mission.mission.value)
        verification = VerificationResult(status=VerificationStatus.VERIFIED)
        
        # Proactive Executive Secretary Policy: Execute routine/safe tasks automatically; intercept sensitive/conflicting actions
        is_safe_decision = audit.decision in [AuditClassification.SAFE_NEW_MEETING, AuditClassification.RECURRING, AuditClassification.RESCHEDULE] or mission.mission == MissionAction.QUERY
        is_safe_risk = audit.risk_level == ExecutiveRiskLevel.ROUTINE_SAFE or audit.decision == AuditClassification.SAFE_NEW_MEETING
        
        should_execute = is_safe_decision and is_safe_risk
        
        if should_execute:
            # Execute tool actions autonomously via CalendarExecutor
            execution = CalendarExecutorAgent.execute(mission=mission)
            memory_manager.record_execution(execution, session_id=session_id)
            
            # Independent Execution Verifier audits storage and API proof
            verification = ExecutionVerifierAgent.verify(mission=mission, execution=execution)
            memory_manager.record_verification(verification, session_id=session_id)
        else:
            logger.warning(f"🛡️ Executive Guardrail Intercepted Execution: Decision '{audit.decision.value}' | Risk '{audit.risk_level.value}'")
            execution.success = False
            execution.warnings.append(f"Execution paused by AI Auditor for executive authorization: {audit.reason}")
            verification.status = VerificationStatus.VERIFIED  # Verified protective interception

        # Refresh database events overview post-execution
        updated_events = CalendarTool.list_upcoming_meetings(filter_month=None).get("events", [])

        # 5. AGENT 5: Executive Report Generator (Synthesizes professional communication based on verified proof)
        final_report = ReportGeneratorAgent.generate_report(
            mission=mission,
            audit=audit,
            execution=execution,
            verification=verification,
            existing_events=updated_events
        )
        
        logger.info(f"🏁 SCHEDULING ORCHESTRATOR: Autonomous Executive Pipeline completion verified.")
        return final_report
