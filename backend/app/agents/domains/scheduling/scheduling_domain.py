import json
from typing import Dict, Any, List
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.models import DomainExecutionRequest, DomainType, TaskDefinition
from backend.app.prompts import SCHEDULING_DOMAIN_PROMPT

class SchedulingDomainAgent:
    """
    Scheduling Domain Reasoning Agent.
    Responsibilities: Understand scheduling missions, analyze semantic conflict status, decide whether confirmation is required, and output structured execution requests.
    Strict Rule: NEVER calls tools or APIs directly.
    """
    @staticmethod
    def reason(task: TaskDefinition, context: str = "", raw_prompt: str = "") -> DomainExecutionRequest:
        logger.info(f"📅 SCHEDULING DOMAIN AGENT: Reasoning on task '{task.task_name}' [{task.action}]")
        
        override_words = ["confirm", "force", "insert anyway", "oui", "yes proceed", "ignore warning", "override", "valide", "valider", "yes", "delete all", "mise a jour", "clear"]
        has_override = any(w in raw_prompt.lower() for w in override_words)
        
        # Determine target tool method and parameters without touching external systems
        action = task.action.upper()
        if action in ["CREATE", "INSERT", "INSERT_MEETING"]:
            target = "add_meeting"
            req_confirm = False
        elif action in ["DELETE", "CANCEL", "DELETE_MEETINGS"]:
            target = "delete_meetings"
            req_confirm = not has_override
        else:
            target = "list_upcoming_meetings"
            req_confirm = False

        params = task.parameters or {}
        if target == "delete_meetings":
            target_kw = params.get("title", "")
            if not target_kw and params.get("participants"):
                target_kw = " ".join(params.get("participants"))
            params = {"keyword": target_kw or "all", "date_str": params.get("date")}
        elif target == "add_meeting":
            params = {
                "title": params.get("title", "Executive Meeting"),
                "date_str": params.get("date", "2026-08-24"),
                "time_str": params.get("time", "10:00:00"),
                "description": params.get("description", "Automated AI Agent Schedule")
            }

        return DomainExecutionRequest(
            domain=DomainType.SCHEDULING,
            action_type=action,
            target_tool="CalendarTool",
            parameters=params,
            requires_user_confirmation=req_confirm,
            confirmation_reason=f"Sensitive deletion action on records matching '{params.get('keyword')}' requires explicit authorization." if req_confirm else None
        )
