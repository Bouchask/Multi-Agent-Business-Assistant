from typing import List, Dict, Any
from loguru import logger
from backend.app.models import TaskDefinition, DomainType, DomainExecutionRequest

class DomainRouterAgent:
    """
    Agent 4: Domain Router
    Responsibilities: Direct tasks to their proper domain reasoning agents (Scheduling, Email, Research).
    Strict Rule: The router NEVER executes business logic or calls APIs.
    """
    @staticmethod
    def route_task(task: TaskDefinition) -> DomainType:
        logger.debug(f"🧭 DOMAIN ROUTER: Routing task '{task.task_name}' [{task.domain.value}]")
        # Ensure strict domain mapping based on task properties
        if task.domain == DomainType.EMAIL or "email" in task.task_name.lower() or "mail" in task.action.lower():
            return DomainType.EMAIL
        elif task.domain == DomainType.RESEARCH or "search" in task.task_name.lower() or "research" in task.action.lower():
            return DomainType.RESEARCH
        return DomainType.SCHEDULING
