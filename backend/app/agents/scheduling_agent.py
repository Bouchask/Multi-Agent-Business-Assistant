from loguru import logger
from backend.app.workflows.engine import ExecutiveWorkflowEngine

class SchedulingAgent:
    """
    Entry point bridge connecting legacy chatbot interface to the 
    autonomous multi-agent Executive Operating System workflow engine.
    """
    def __init__(self):
        self.engine = ExecutiveWorkflowEngine(session_id="chat_ui_session")

    def run(self, user_command: str, session_id: str = "default_session", **kwargs) -> str:
        logger.info(f"👔 AI EXECUTIVE OPERATING SYSTEM Entry Point: Executing workflow for command -> '{user_command}'")
        engine = ExecutiveWorkflowEngine(session_id=session_id)
        return engine.run_workflow(user_command)

scheduling_agent = SchedulingAgent()
