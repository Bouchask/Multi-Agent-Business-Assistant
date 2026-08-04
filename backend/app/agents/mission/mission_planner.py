import json
import re
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.models import StructuredMission, DomainType
from backend.app.core.state import MissionState, ExecutionMode
from backend.app.prompts import MISSION_PLANNER_PROMPT

class MissionPlannerAgent:
    """
    Agent 2: Mission Planner
    Responsibilities: Convert natural text into structured business mission JSON (objectives, intent, entities, constraints).
    Strict Rule: Output only structured mission JSON. Never call tools.
    """
    @staticmethod
    def create_mission(user_prompt: str, supervisor_context: Dict[str, Any] = None) -> StructuredMission:
        logger.info(f"💼 MISSION PLANNER: Structuring mission from input: '{user_prompt}'")
        try:
            res = llm_client.complete(
                messages=[
                    {"role": "system", "content": MISSION_PLANNER_PROMPT},
                    {"role": "user", "content": f"User Request: '{user_prompt}'\nSupervisor Context: {json.dumps(supervisor_context or {})}"}
                ],
                temperature=0.1
            )
            raw = res.get("content", "{}").strip()
            if raw.startswith("```json"):
                raw = raw[7:-3].strip()
            elif raw.startswith("```"):
                raw = raw[3:-3].strip()
            data = json.loads(raw)
            logger.info(f"✨ MISSION PLANNER SCHEMA: {data}")
            
            domains = [DomainType(d) for d in data.get("required_domains", ["SCHEDULING"]) if d in DomainType.__members__]
            if not domains:
                domains = [DomainType.SCHEDULING]
                
            return StructuredMission(
                raw_input=user_prompt,
                objective=data.get("objective", f"Execute directive for '{user_prompt[:30]}'"),
                intent=data.get("intent", "EXECUTE"),
                entities=data.get("entities", {}),
                constraints=data.get("constraints", ["Prevent double-booking", "Require authorization for destructive actions"]),
                dependencies=data.get("dependencies", ["Check existing calendar records"]),
                required_domains=domains,
                execution_mode=ExecutionMode.SEQUENTIAL,
                state=MissionState.PLANNED
            )
        except Exception as e:
            logger.warning(f"Mission Planner parsing fallback: {e}")
            low = user_prompt.lower()
            intent = "DELETE" if any(w in low for w in ["delete", "supprime", "cancel", "clear"]) else ("CREATE" if any(w in low for w in ["insert", "add", "book", "schedule"]) else "QUERY")
            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', user_prompt)
            return StructuredMission(
                raw_input=user_prompt,
                objective=f"Process {intent} directive for user request",
                intent=intent,
                entities={"title": user_prompt[:35], "emails": emails, "date": "2026-08-24", "time": "10:00:00"},
                required_domains=[DomainType.SCHEDULING, DomainType.EMAIL] if emails else [DomainType.SCHEDULING],
                state=MissionState.PLANNED
            )
