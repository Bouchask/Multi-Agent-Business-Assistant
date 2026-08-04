from typing import List, Dict, Any, Optional
from loguru import logger
from backend.app.domain.scheduling.orchestrator import SchedulingOrchestrator

class SchedulingAgent:
    """
    Enterprise Refactored Scheduling Agent.
    Delegates all domain processing, entity extraction, semantic audit guardrails, tool execution,
    independent verification, and markdown report synthesis directly to the SchedulingOrchestrator.
    """
    def run(self, instruction: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        logger.info(f"📅 SCHEDULING AGENT Entry Point: Re-routing to Enterprise SchedulingOrchestrator -> '{instruction}'")
        return SchedulingOrchestrator.execute_workflow(raw_instruction=instruction, history=history)

scheduling_agent = SchedulingAgent()
