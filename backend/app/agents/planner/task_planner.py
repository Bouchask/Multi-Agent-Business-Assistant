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
    Strict Rule: Never execute tasks; only emit typed TaskDefinition arrays with exact preserved parameters & filters.
    """
    @staticmethod
    def break_into_tasks(mission: StructuredMission) -> List[TaskDefinition]:
        logger.info(f"📑 TASK PLANNER: Breaking mission '{mission.intent}' into actionable task steps...")
        
        # If mission is a calendar query, guarantee a direct LIST_MEETINGS task with uncorrupted filters
        if mission.intent in ["QUERY", "QUERY_MEETINGS", "LIST", "LIST_MEETINGS"] or ("list" in mission.raw_input.lower() and not any(w in mission.raw_input.lower() for w in ["delete", "insert", "add", "remove", "supprime"])):
            logger.info("📑 TASK PLANNER: Generating verified filtered query task with exact mission filters.")
            return [
                TaskDefinition(
                    task_id="step_1",
                    task_name="Execute filtered calendar query",
                    domain=DomainType.SCHEDULING,
                    action="LIST_MEETINGS",
                    parameters=mission.filters if mission.filters else mission.entities
                )
            ]

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
                params = item.get("parameters", mission.entities)
                # Merge in preserved filters if this is a query or inspection step
                if mission.filters and any(w in str(item.get("action", "")).upper() for w in ["QUERY", "LIST", "CHECK", "AUDIT"]):
                    params = {**params, **mission.filters}
                    
                tasks.append(TaskDefinition(
                    task_id=str(item.get("task_id", f"step_{len(tasks)+1}")),
                    task_name=str(item.get("task_name", "Execute domain step")),
                    domain=d_val,
                    action=str(item.get("action", mission.intent)),
                    parameters=params
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
