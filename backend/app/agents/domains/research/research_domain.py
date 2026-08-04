from loguru import logger
from backend.app.models import DomainExecutionRequest, DomainType, TaskDefinition

class ResearchDomainAgent:
    """
    Research Domain Reasoning Agent.
    Responsibilities: Formulate web query search targets and intelligence gathering parameters.
    Strict Rule: NEVER calls search engines directly; outputs structured DomainExecutionRequest.
    """
    @staticmethod
    def reason(task: TaskDefinition, context: str = "") -> DomainExecutionRequest:
        logger.info(f"🌐 RESEARCH DOMAIN AGENT: Structuring search strategy for task '{task.task_name}'")
        params = task.parameters or {}
        query = params.get("query") or params.get("title") or "Executive corporate intelligence"
        
        return DomainExecutionRequest(
            domain=DomainType.RESEARCH,
            action_type="EXECUTE_SEARCH",
            target_tool="WebSearchTool",
            parameters={"query": query, "max_results": 5},
            requires_user_confirmation=False
        )
