import json
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.models import StructuredMission
from backend.app.prompts import SUPERVISOR_PROMPT

class ExecutiveSupervisorAgent:
    """
    Agent 1: Executive Supervisor
    Responsibilities: Receive goal, understand objective, decide workflow strategy, and delegate to Mission Planner.
    Strict Rule: Never call tools or execute business logic.
    """
    @staticmethod
    def delegate_goal(user_goal: str) -> Dict[str, Any]:
        logger.info(f"👔 EXECUTIVE SUPERVISOR: Analyzing strategic corporate directive: '{user_goal}'")
        try:
            res = llm_client.complete(
                messages=[
                    {"role": "system", "content": SUPERVISOR_PROMPT},
                    {"role": "user", "content": f"Executive Goal: '{user_goal}'\nProvide strategic workflow delegation JSON."}
                ],
                temperature=0.1
            )
            raw = res.get("content", "{}").strip()
            if raw.startswith("```json"):
                raw = raw[7:-3].strip()
            elif raw.startswith("```"):
                raw = raw[3:-3].strip()
            data = json.loads(raw)
            logger.info(f"👔 SUPERVISOR STRATEGY: {data}")
            return data
        except Exception as e:
            logger.warning(f"Supervisor parsing fallback: {e}")
            return {"status": "DELEGATED_TO_MISSION_PLANNER", "strategic_priority": "HIGH", "raw_goal": user_goal}
