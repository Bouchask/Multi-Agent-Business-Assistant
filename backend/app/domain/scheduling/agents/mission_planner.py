import json
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.domain.scheduling.models import MissionProfile, MissionAction, MissionPriority, MeetingEntities
from backend.app.domain.scheduling.prompts import MISSION_PLANNER_PROMPT

class MissionPlannerAgent:
    """
    Agent 1: Executive Mission Planner
    Responsibilities: Understand user intent, extract entities, build mission schema, determine required agents.
    Strict Rule: Never call tools. Output MissionProfile only.
    """
    @staticmethod
    def plan_mission(raw_command: str, memory_context: str = "") -> MissionProfile:
        logger.info(f"💼 MISSION PLANNER: Analyzing executive request: '{raw_command}'")
        try:
            res = llm_client.complete(
                messages=[
                    {"role": "system", "content": MISSION_PLANNER_PROMPT},
                    {"role": "user", "content": f"Working Memory Context:\n{memory_context}\n\nExecutive Request: '{raw_command}'"}
                ],
                temperature=0.1
            )
            raw_json = res.get("content", "{}").strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:-3].strip()
            elif raw_json.startswith("```"):
                raw_json = raw_json[3:-3].strip()
            
            data = json.loads(raw_json)
            logger.info(f"✨ MISSION PLANNER SCHEMA OUTPUT: {data}")
            return MissionProfile(**data)
        except Exception as e:
            logger.warning(f"Mission Planner JSON parser fallback: {e}")
            is_create = any(w in raw_command.lower() for w in ["insert", "add", "book", "create", "schedule"])
            import re
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', raw_command)
            return MissionProfile(
                mission=MissionAction.CREATE if is_create else MissionAction.QUERY,
                priority=MissionPriority.NORMAL,
                entities=MeetingEntities(title=raw_command[:30], emails=emails),
                reasoning=["Deducted intent via resilient structured backup analysis"]
            )
