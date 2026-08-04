# Core AI OS Infrastructure
from enum import Enum
from loguru import logger
from typing import Optional, Any, Dict, List

class MissionState(str, Enum):
    NEW = "NEW"
    PLANNED = "PLANNED"
    TASKS_CREATED = "TASKS_CREATED"
    ROUTED = "ROUTED"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ExecutionMode(str, Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"

class DomainType(str, Enum):
    SCHEDULING = "SCHEDULING"
    EMAIL = "EMAIL"
    RESEARCH = "RESEARCH"
    CRM = "CRM"
    FINANCE = "FINANCE"
    ANALYTICS = "ANALYTICS"
    GENERAL = "GENERAL"

def log_state_transition(mission_id: str, old_state: MissionState, new_state: MissionState, detail: str = ""):
    logger.info(f"🔄 MISSION STATE CHANGE [{mission_id}]: `{old_state.value}` ➔ `{new_state.value}` | {detail}")
