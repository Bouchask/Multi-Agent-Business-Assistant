# SQLAlchemy DB Record Models (Required for relational mapper resolution)
from backend.app.models.user import User
from backend.app.models.role import Role
from backend.app.models.file_record import FileRecord
from backend.app.models.project import Project
from backend.app.models.task import Task
from backend.app.models.meeting import Meeting
from backend.app.models.chat_history import ChatHistory

# AI Executive OS Pydantic Communication Models
from backend.app.core.state import MissionState, ExecutionMode, DomainType
from backend.app.models.base import StructuredMission, TaskDefinition, DomainExecutionRequest, ToolExecutionResult, VerificationReport, ExecutiveOutput, EntityExtraction
from backend.app.models.memory import WorkingMemoryModel

__all__ = [
    # Relational Models
    "User",
    "Role",
    "FileRecord",
    "Project",
    "Task",
    "Meeting",
    "ChatHistory",
    # Agent OS Typed Models
    "MissionState",
    "ExecutionMode",
    "DomainType",
    "StructuredMission",
    "TaskDefinition",
    "DomainExecutionRequest",
    "ToolExecutionResult",
    "VerificationReport",
    "ExecutiveOutput",
    "EntityExtraction",
    "WorkingMemoryModel"
]
