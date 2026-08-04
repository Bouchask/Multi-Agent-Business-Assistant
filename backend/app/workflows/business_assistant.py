from typing import Dict, Any, List, Optional
from loguru import logger
from backend.app.workflows.engine import ExecutiveWorkflowEngine

class MultiAgentOrchestrator:
    """
    Enterprise Orchestrator Bridge.
    Connects incoming HTTP API requests directly to the autonomous 10-layer
    Agentic AI Executive Operating System workflow engine.
    """
    @staticmethod
    def execute(user_input: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        logger.info(f"👔 MULTI-AGENT ORCHESTRATOR: Initiating Agentic AI OS workflow for -> '{user_input[:50]}...'")
        
        # Route directly into the ExecutiveWorkflowEngine state machine
        engine = ExecutiveWorkflowEngine(session_id="active_browser_session")
        reply = engine.run_workflow(user_command=user_input)
        
        # Determine appropriate UI badge display based on domain content
        low_cmd = user_input.lower()
        if any(w in low_cmd for w in ["email", "mail", "send"]):
            agent_badge = "EMAIL & SCHEDULING AGENT"
        elif any(w in low_cmd for w in ["search", "web", "research", "find"]):
            agent_badge = "RESEARCH & INTELLIGENCE AGENT"
        elif any(w in low_cmd for w in ["delete", "meet", "schedule", "calendar", "list"]):
            agent_badge = "EXECUTIVE SCHEDULING AGENT"
        else:
            agent_badge = "EXECUTIVE SUPERVISOR AI"

        return {
            "success": True,
            "reply": reply,
            "agent_triggered": agent_badge,
            "workflow": "Agentic AI Executive Operating System (State Machine)"
        }
