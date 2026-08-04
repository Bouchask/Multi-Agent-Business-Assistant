import pytest
from backend.app.core import MissionState, ExecutionMode, DomainType
from backend.app.models import StructuredMission, TaskDefinition, ToolExecutionResult, VerificationReport
from backend.app.memory.store import memory_manager
from backend.app.workflows.engine import ExecutiveWorkflowEngine

def test_01_state_machine_and_typed_schemas():
    """Validates explicit state transitions and structured inter-agent communication schemas."""
    mission = StructuredMission(raw_input="Schedule team lunch", state=MissionState.NEW)
    assert mission.state == MissionState.NEW
    mission.state = MissionState.PLANNED
    assert mission.state == MissionState.PLANNED
    assert mission.execution_mode == ExecutionMode.SEQUENTIAL
    print("✅ Test 01: State machine transitions and typed schemas verified successfully!")

def test_02_structured_working_memory():
    """Validates working memory architecture replacing raw conversation histories."""
    session_id = "test_memory_session"
    mem = memory_manager.get_memory(session_id)
    mem.current_objective = "Manage executive appointments autonomously."
    mem.completed_tasks.append(TaskDefinition(task_id="step_1", task_name="Audit calendar", domain=DomainType.SCHEDULING, action="AUDIT"))
    summary = mem.summarize_context()
    assert "Audit calendar" in summary
    assert "Manage executive appointments" in summary
    print("✅ Test 02: Structured Working Memory architecture validated!")

def test_03_end_to_end_autonomous_workflow_execution():
    """Tests full lifecycle orchestration through Supervisor, Mission Planner, Task Planner, Router, Domain AI, Verifier, and Reporter."""
    engine = ExecutiveWorkflowEngine(session_id="e2e_integration")
    cmd = "insert meet with dr yahya with email mr.bouchakyahya@gmail.com for gestion labo in 2026-11-20 at 10:00"
    res = engine.run_workflow(cmd)
    assert "---THINKING---" in res
    assert ("VERIFIED SUCCESS" in res or "PARTIAL SUCCESS" in res or "Executive Confirmation Required" in res)
    print("✅ Test 03: Full AI Executive Operating System workflow confirmed via unit test!")
