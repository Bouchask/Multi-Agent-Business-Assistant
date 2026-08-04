from loguru import logger

class SchedulingAgent:
    """
    Entry point bridge connecting legacy chatbot interface to the 
    autonomous multi-agent Executive Operating System workflow engine.
    """
    def run(self, user_command: str, session_id: str = "default_session", **kwargs) -> str:
        logger.info(f"👔 AI EXECUTIVE OPERATING SYSTEM Entry Point: Executing workflow for command -> '{user_command}'")
        # Local import to prevent circular dependency with agents package initialization
        from backend.app.workflows.engine import ExecutiveWorkflowEngine
        engine = ExecutiveWorkflowEngine(session_id=session_id)
        return engine.run_workflow(user_command)

scheduling_agent = SchedulingAgent()
