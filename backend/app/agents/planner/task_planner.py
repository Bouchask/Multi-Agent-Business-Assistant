import json
from typing import List
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.models import StructuredMission, TaskDefinition, DomainType
from backend.app.prompts import TASK_PLANNER_PROMPT

class TaskPlannerAgent:
    """
    Agent 3: Task Planner
    Responsibilities: Break one structured mission into granular, sequential or parallel executable tasks.
    Strict Rule: Never execute tasks; only emit typed TaskDefinition arrays.
    """
    @staticmethod
    def break_into_tasks(mission: StructuredMission) -> List[TaskDefinition]:
        logger.info(f"📑 TASK PLANNER: Breaking mission '{mission.intent}' into actionable task steps...")
        try:
            res = llm_client.complete(
                messages=[
                    {"role": "system", "content": TASK_PLANNER_PROMPT},
                    {"role": "user", "content": f"Mission Profile:\n{mission.model_dump_json(indent=2)}\n\nEmit JSON task array."}
                ],
                temperature=0.1
            )
            raw = res.get("content", "[]").strip()
            if raw.startswith("```json"):
                raw = raw[7:-3].strip()
            elif raw.startswith("```"):
                raw = raw[3:-3].strip()
            data = json.loads(raw)
            logger.info(f"📑 GENERATED TASKS: {len(data)} granular actions")
            
            tasks = []
            for item in data:
                d_str = item.get("domain", "SCHEDULING")
                d_val = DomainType(d_str) if d_str in DomainType.__members__ else DomainType.SCHEDULING
                tasks.append(TaskDefinition(
                    task_id=str(item.get("task_id", f"step_{len(tasks)+1}")),
                    task_name=str(item.get("task_name", "Execute domain step")),
                    domain=d_val,
                    action=str(item.get("action", mission.intent)),
                    parameters=item.get("parameters", mission.entities)
                ))
            if tasks:
                return tasks
        except Exception as e:
            logger.warning(f"Task Planner parsing fallback: {e}")

        # Reliable standard executive workflow breakdown fallback
        tasks = [
            TaskDefinition(task_id="step_1", task_name="Evaluate calendar conflict & risk status", domain=DomainType.SCHEDULING, action="AUDIT", parameters=mission.entities),
            TaskDefinition(task_id="step_2", task_name="Execute relational DB & GCal OAuth alteration", domain=DomainType.SCHEDULING, action=mission.intent, parameters=mission.entities)
        ]
        if mission.entities.get("emails") and mission.intent in ["CREATE", "UPDATE", "CONFIRM"]:
            tasks.append(TaskDefinition(task_id="step_3", task_name="Dispatch confirmed calendar invitation email", domain=DomainType.EMAIL, action="SEND_INVITATION", parameters=mission.entities))
        return tasks
