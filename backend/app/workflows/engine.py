import time
from typing import Dict, Any, List, Optional
from loguru import logger

from backend.app.core.state import MissionState, DomainType, log_state_transition
from backend.app.core.exceptions import AgentOSException, VerificationFailedError, UserCancellationException
from backend.app.models import StructuredMission, TaskDefinition, DomainExecutionRequest, ToolExecutionResult, VerificationReport
from backend.app.memory.store import memory_manager
from backend.app.agents import (
    ExecutiveSupervisorAgent,
    MissionPlannerAgent,
    TaskPlannerAgent,
    DomainRouterAgent,
    SchedulingDomainAgent,
    EmailDomainAgent,
    ResearchDomainAgent,
    ExecutionVerifierAgent,
    ExecutiveReporterAgent
)
from backend.app.tools.calendar_tool import CalendarTool
from backend.app.tools.gmail_tool import GmailTool
from backend.app.tools.search.web_search_tool import WebSearchTool
from backend.app.tools.database.db_tool import DatabaseTool

class ExecutiveWorkflowEngine:
    """
    Enterprise Agentic AI Executive Operating System Workflow Engine.
    Strict separation of concerns: Pure Python orchestration driving explicit state machine transitions
    and tool dependency injection. Zero business logic or string heuristics embedded.
    """
    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.memory = memory_manager.get_memory(session_id)
        
        # Dependency Injection Register for Tool Layer (Pure execution, returning structured dicts/JSON)
        self.tool_registry: Dict[str, Any] = {
            "CalendarTool": CalendarTool,
            "GmailTool": GmailTool,
            "WebSearchTool": WebSearchTool,
            "DatabaseTool": DatabaseTool
        }

    def run_workflow(self, user_command: str) -> str:
        start_t = time.time()
        logger.info(f"🚀 EXECUTIVE WORKFLOW ENGINE: Starting mission execution lifecycle for session '{self.session_id}'")
        
        # STATE TRANSITION 1: NEW
        mission = StructuredMission(raw_input=user_command, state=MissionState.NEW)
        self.memory.active_mission = mission
        log_state_transition(mission.mission_id, MissionState.NEW, MissionState.PLANNED, "Engaging Executive Supervisor & Mission Planner")

        try:
            # Step 1: Executive Supervisor strategic governance delegation
            supervisor_strategy = ExecutiveSupervisorAgent.delegate_goal(user_command)
            
            # Step 2: Mission Planner constructs typed StructuredMission
            mission = MissionPlannerAgent.create_mission(user_command, supervisor_context=supervisor_strategy)
            mission.state = MissionState.PLANNED
            self.memory.active_mission = mission
            
            # STATE TRANSITION 2: PLANNED ➔ TASKS_CREATED
            log_state_transition(mission.mission_id, MissionState.PLANNED, MissionState.TASKS_CREATED, "Task Planner breaking mission into executable steps")
            tasks = TaskPlannerAgent.break_into_tasks(mission)
            self.memory.pending_tasks = tasks
            mission.state = MissionState.TASKS_CREATED

            # STATE TRANSITION 3: TASKS_CREATED ➔ ROUTED
            log_state_transition(mission.mission_id, MissionState.TASKS_CREATED, MissionState.ROUTED, "Domain Router directing tasks to specialized domain reasoning agents")
            routed_tasks: List[TaskDefinition] = []
            for t in tasks:
                t.domain = DomainRouterAgent.route_task(t)
                routed_tasks.append(t)
            mission.state = MissionState.ROUTED

            # STATE TRANSITION 4: ROUTED ➔ EXECUTING
            log_state_transition(mission.mission_id, MissionState.ROUTED, MissionState.EXECUTING, "Domain Agents generating structured tool requests & evaluating confirmation guardrails")
            mission.state = MissionState.EXECUTING
            tool_results: List[ToolExecutionResult] = []
            requires_pause_message: Optional[str] = None

            for task in routed_tasks:
                # Delegate reasoning to specialized Domain AI
                if task.domain == DomainType.EMAIL:
                    exec_req = EmailDomainAgent.reason(task)
                elif task.domain == DomainType.RESEARCH:
                    exec_req = ResearchDomainAgent.reason(task)
                else:
                    exec_req = SchedulingDomainAgent.reason(task, raw_prompt=user_command)

                # Proactive Executive Secretary Guardrail: Intercept if action requires authorization
                if exec_req.requires_user_confirmation:
                    logger.warning(f"🛡️ Executive Guardrail Intercepted Task '{task.task_name}': {exec_req.confirmation_reason}")
                    requires_pause_message = f"Before proceeding with this sensitive deletion or record modification, I want to confirm: **would you like me to execute '{exec_req.action_type}' for records matching your directive?** Please reply to confirm authorization."
                    break

                # Execute Tool via Dependency Injection Registry
                tool_cls = self.tool_registry.get(exec_req.target_tool)
                if tool_cls:
                    logger.info(f"⚙️ EXECUTING TOOL: `{exec_req.target_tool}` -> `{exec_req.action_type}` with params {exec_req.parameters}")
                    res_payload: Dict[str, Any] = {}
                    try:
                        if exec_req.target_tool == "CalendarTool":
                            if exec_req.action_type in ["CREATE", "INSERT", "INSERT_MEETING", "ADD_MEETING"]:
                                res_payload = tool_cls.add_meeting(title=exec_req.parameters.get("title", "Meeting"), date_str=exec_req.parameters.get("date", "2026-08-24"), time_str=exec_req.parameters.get("time", "10:00:00"), description=exec_req.parameters.get("description", ""))
                            elif exec_req.action_type in ["DELETE", "CANCEL", "DELETE_MEETINGS"]:
                                res_payload = tool_cls.delete_meetings(keyword=exec_req.parameters.get("keyword", ""), date_str=exec_req.parameters.get("date_str"))
                            else:
                                res_payload = {"success": True, "action": "LIST_QUERY", "events": tool_cls.list_upcoming_meetings().get("events", [])}
                        elif exec_req.target_tool == "GmailTool":
                            res_payload = tool_cls.send_email(recipient=exec_req.parameters.get("recipient", "user@local.domain"), subject=exec_req.parameters.get("subject", "Invite"), body=exec_req.parameters.get("body", ""))
                        elif exec_req.target_tool == "WebSearchTool":
                            res_payload = tool_cls.execute_search(query=exec_req.parameters.get("query", ""))
                        
                        tool_res = ToolExecutionResult(
                            tool_name=exec_req.target_tool,
                            success=bool(res_payload.get("success", True)),
                            action_performed=exec_req.action_type,
                            data=res_payload
                        )
                    except Exception as ex_tool:
                        tool_res = ToolExecutionResult(tool_name=exec_req.target_tool, success=False, errors=[str(ex_tool)])
                    
                    tool_results.append(tool_res)
                    self.memory.tool_results.append(tool_res)
                    task.is_completed = tool_res.success
                    self.memory.completed_tasks.append(task)

            if requires_pause_message:
                mission.state = MissionState.VERIFYING # Verified pause status
                return (
                    f"---THINKING---\n"
                    f"**Mission Directive**: `[SENSITIVE_GUARDRAIL_INTERCEPTION]` | **State**: `PAUSED_FOR_AUTHORIZATION`  \n"
                    f"**Executive Reasoning**:  \n  - 💭 *Intercepted sensitive or destructive workflow step to protect existing corporate records.*  \n"
                    f"---THINKING_END---\n\n"
                    f"🛡️ **Executive Confirmation Required**\n\n{requires_pause_message}"
                )

            # STATE TRANSITION 5: EXECUTING ➔ VERIFYING
            log_state_transition(mission.mission_id, MissionState.EXECUTING, MissionState.VERIFYING, "Execution Verifier independently auditing database storage & API return IDs")
            mission.state = MissionState.VERIFYING
            verification = ExecutionVerifierAgent.verify(mission=mission, tool_results=tool_results)
            self.memory.verifications.append(verification)

            # STATE TRANSITION 6: VERIFYING ➔ COMPLETED (or FAILED)
            final_state = MissionState.COMPLETED if verification.is_verified else MissionState.FAILED
            log_state_transition(mission.mission_id, MissionState.VERIFYING, final_state, f"Executive Reporter generating final response based on {final_state.value} audit")
            mission.state = final_state
            self.memory.execution_status = final_state

            final_markdown = ExecutiveReporterAgent.synthesize(mission=mission, tool_results=tool_results, verification=verification)
            logger.info(f"🏁 EXECUTIVE WORKFLOW ENGINE: Completed full operational lifecycle in {round(time.time() - start_t, 3)}s.")
            return final_markdown

        except Exception as err:
            logger.exception(f"Critical exception in Executive Workflow Engine: {err}")
            log_state_transition(mission.mission_id, mission.state, MissionState.FAILED, f"Recoverable fallback: {str(err)}")
            mission.state = MissionState.FAILED
            return f"### ⚠️ System Notification\nThe Executive Operating System encountered an error during workflow transition (`{str(err)}`). State has been safely stabilized without unauthorized modifications."
