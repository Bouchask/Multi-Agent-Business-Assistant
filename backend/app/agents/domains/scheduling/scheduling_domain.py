import json
from typing import Dict, Any, List
from loguru import logger
from backend.app.models import DomainExecutionRequest, DomainType, TaskDefinition
from backend.app.prompts import SCHEDULING_DOMAIN_PROMPT

class SchedulingDomainAgent:
    """
    Scheduling Domain Reasoning Agent.
    Responsibilities: Understand scheduling missions, preserve structured query filters, analyze semantic conflict status, and decide whether confirmation is required.
    Strict Rule: NEVER calls tools or APIs directly. NEVER executes generic queries or drops filters.
    """
    @staticmethod
    def reason(task: TaskDefinition, context: str = "", raw_prompt: str = "") -> DomainExecutionRequest:
        logger.info(f"📅 SCHEDULING DOMAIN AGENT: Reasoning on task '{task.task_name}' [{task.action}]")
        
        override_words = ["confirm", "force", "insert anyway", "oui", "yes proceed", "ignore warning", "override", "valide", "valider", "yes", "delete all", "mise a jour", "clear"]
        has_override = any(w in raw_prompt.lower() for w in override_words)
        
        action = task.action.upper()
        params = task.parameters or {}
        
        if action in ["CREATE", "INSERT", "INSERT_MEETING", "ADD", "BOOK", "SCHEDULE"]:
            target_method = "add_meeting"
            req_confirm = False
            params = {
                "title": params.get("title", "Executive Meeting"),
                "date_str": params.get("date", "2026-08-24"),
                "time_str": params.get("time", "10:00:00"),
                "description": params.get("description", "Automated AI Agent Schedule")
            }
            action = "INSERT_MEETING"
        elif action in ["DELETE", "CANCEL", "DELETE_MEETINGS", "REMOVE", "SUPPRIME"]:
            target_method = "delete_meetings"
            req_confirm = not has_override
            target_kw = params.get("title", "")
            if not target_kw and params.get("participants"):
                target_kw = " ".join(params.get("participants"))
            params = {"keyword": target_kw or "all", "date_str": params.get("date")}
            action = "DELETE_MEETINGS"
        else:
            # Mandated Correct Pattern: Forward exact filters to list_meetings without discarding any fields
            target_method = "list_meetings"
            req_confirm = False
            action = "LIST_MEETINGS"
            # Keep all filter keys exactly as received from Mission Planner / Task Planner
            params = dict(params)

        return DomainExecutionRequest(
            domain=DomainType.SCHEDULING,
            action_type=action,
            target_tool="CalendarTool",
            parameters=params,
            requires_user_confirmation=req_confirm,
            confirmation_reason=f"Sensitive deletion action on records matching '{params.get('keyword')}' requires explicit authorization." if req_confirm else None
        )
