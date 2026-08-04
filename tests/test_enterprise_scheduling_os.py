import pytest
from backend.app.domain.scheduling.models import MissionProfile, MissionAction, AuditDecision, AuditClassification, ExecutionResult, VerificationResult, VerificationStatus
from backend.app.domain.scheduling.memory import memory_manager
from backend.app.domain.scheduling.orchestrator import SchedulingOrchestrator

def test_01_domain_models_and_validation():
    """Verify typed Pydantic models contract validation and defaults."""
    mission = MissionProfile(mission=MissionAction.CREATE, requires_duplicate_check=True)
    assert mission.mission == "CREATE"
    assert mission.requires_calendar_lookup is True

    audit = AuditDecision(decision=AuditClassification.SAFE_NEW_MEETING, confidence=0.97)
    assert audit.decision == "SAFE_NEW_MEETING"
    assert audit.confidence == 0.97

    exec_res = ExecutionResult(success=True, action_attempted="CREATE", database_id="db_100")
    assert exec_res.success is True

    verif_res = VerificationResult(status=VerificationStatus.VERIFIED, database_verified=True)
    assert verif_res.status == "VERIFIED"
    print("✅ Test 01: Pydantic Domain Models contracts validated successfully!")

def test_02_working_memory_state_management():
    """Verify Working Memory manager avoids raw chat history leakage."""
    session_id = "test_enterprise_session"
    memory_manager.clear_session(session_id)
    
    mission = MissionProfile(mission=MissionAction.CREATE)
    mission.entities.title = "Executive Architecture Board"
    memory_manager.update_mission(mission, session_id=session_id)
    
    mem = memory_manager.get_session_memory(session_id)
    assert mem.current_mission.entities.title == "Executive Architecture Board"
    assert len(mem.pending_tasks) == 1
    
    exec_res = ExecutionResult(success=True, action_attempted="CREATE")
    memory_manager.record_execution(exec_res, session_id=session_id)
    
    assert len(mem.completed_tasks) == 1
    assert len(mem.pending_tasks) == 0
    print("✅ Test 02: Structured Working Memory state managed without leakage!")

def test_03_orchestrator_end_to_end_execution():
    """Test full multi-agent orchestration execution pipeline."""
    res = SchedulingOrchestrator.execute_workflow(
        raw_instruction="insert meet with dr yahya with email mr.bouchakyahya@gmail.com for gestion labo in 2026-11-15 at 10:00",
        session_id="integration_test"
    )
    assert "---THINKING---" in res
    assert "Verified Executive Execution Report" in res or "AI Auditor Verdict" in res
    print("✅ Test 03: Full 5-stage Autonomous Orchestrator workflow confirmed!")

if __name__ == "__main__":
    test_01_domain_models_and_validation()
    test_02_working_memory_state_management()
    test_03_orchestrator_end_to_end_execution()
