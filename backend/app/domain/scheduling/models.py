from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class MissionAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    QUERY = "QUERY"
    CONFIRM = "CONFIRM"
    CANCEL = "CANCEL"

class MissionPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"

class AuditClassification(str, Enum):
    SAFE_NEW_MEETING = "SAFE_NEW_MEETING"
    DUPLICATE = "DUPLICATE"
    CONFLICT = "CONFLICT"
    RECURRING = "RECURRING"
    RESCHEDULE = "RESCHEDULE"
    NEED_CONFIRMATION = "NEED_CONFIRMATION"

class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"

class MeetingEntities(BaseModel):
    title: str = Field(default="Executive Meeting", description="Title of the event")
    participants: List[str] = Field(default_factory=list, description="List of participant names")
    emails: List[str] = Field(default_factory=list, description="List of participant emails")
    date: str = Field(default="2026-08-24", description="Target calendar date in YYYY-MM-DD format")
    time: str = Field(default="10:00:00", description="Target start time in 24h format")
    duration: str = Field(default="60", description="Duration in minutes")
    location: str = Field(default="Corporate AI Office", description="Meeting room or link")
    description: str = Field(default="", description="Agenda or summary description")

class MissionProfile(BaseModel):
    mission: MissionAction = Field(default=MissionAction.QUERY)
    requires_calendar_lookup: bool = True
    requires_duplicate_check: bool = True
    requires_conflict_check: bool = True
    requires_confirmation: bool = False
    priority: MissionPriority = Field(default=MissionPriority.NORMAL)
    entities: MeetingEntities = Field(default_factory=MeetingEntities)
    reasoning: List[str] = Field(default_factory=list)

class AuditDecision(BaseModel):
    decision: AuditClassification = Field(default=AuditClassification.SAFE_NEW_MEETING)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reason: str = Field(default="No semantic conflict detected.")
    conversational_message: Optional[str] = None
    recommended_slot: Optional[Dict[str, str]] = None

class ExecutionResult(BaseModel):
    success: bool = False
    action_attempted: str = ""
    database_id: Optional[str] = None
    event_id: Optional[str] = None
    calendar_url: Optional[str] = None
    gmail_message_id: Optional[str] = None
    gmail_recipient: Optional[str] = None
    gmail_delivery_mode: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    execution_time: float = 0.0

class VerificationResult(BaseModel):
    status: VerificationStatus = Field(default=VerificationStatus.VERIFIED)
    database_verified: bool = False
    calendar_verified: bool = False
    gmail_verified: bool = False
    audit_notes: List[str] = Field(default_factory=list)
    discrepancy_details: List[str] = Field(default_factory=list)

class WorkingMemory(BaseModel):
    session_id: str = "default_session"
    current_mission: Optional[MissionProfile] = None
    audit_decision: Optional[AuditDecision] = None
    execution_result: Optional[ExecutionResult] = None
    verification_result: Optional[VerificationResult] = None
    completed_tasks: List[str] = Field(default_factory=list)
    pending_tasks: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    previous_decisions: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
