from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.core.state import MissionState, ExecutionMode, DomainType

class EntityExtraction(BaseModel):
    objective: str = Field(default="Executive Goal", description="Primary objective")
    intent: str = Field(default="EXECUTE", description="Action intent")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted domain entities")
    constraints: List[str] = Field(default_factory=list, description="Execution constraints and safety parameters")
    dependencies: List[str] = Field(default_factory=list, description="Prerequisite conditions")

class StructuredMission(BaseModel):
    mission_id: str = "mis_001"
    raw_input: str = ""
    objective: str = ""
    intent: str = "EXECUTE"
    entities: Dict[str, Any] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    required_domains: List[DomainType] = Field(default_factory=list)
    execution_mode: ExecutionMode = Field(default=ExecutionMode.SEQUENTIAL)
    state: MissionState = Field(default=MissionState.NEW)

class TaskDefinition(BaseModel):
    task_id: str
    task_name: str
    domain: DomainType
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    is_completed: bool = False
    result_data: Optional[Dict[str, Any]] = None

class DomainExecutionRequest(BaseModel):
    domain: DomainType
    action_type: str
    target_tool: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requires_user_confirmation: bool = False
    confirmation_reason: Optional[str] = None

class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool = False
    action_performed: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class VerificationReport(BaseModel):
    is_verified: bool = False
    partial_success: bool = False
    audited_tool: str = ""
    audit_findings: List[str] = Field(default_factory=list)
    discrepancies: List[str] = Field(default_factory=list)

class ExecutiveOutput(BaseModel):
    status_badge: str
    summary: str
    actions_completed: List[str]
    verification_proof: str
    resources_links: List[str]
    next_steps: Optional[str]
    final_markdown: str
