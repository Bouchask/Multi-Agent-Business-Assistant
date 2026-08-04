# Master Specialized Agents Package Init
from backend.app.agents.supervisor import ExecutiveSupervisorAgent
from backend.app.agents.mission import MissionPlannerAgent
from backend.app.agents.planner import TaskPlannerAgent
from backend.app.agents.router import DomainRouterAgent
from backend.app.agents.domains import SchedulingDomainAgent, EmailDomainAgent, ResearchDomainAgent
from backend.app.agents.verification import ExecutionVerifierAgent
from backend.app.agents.reporting import ExecutiveReporterAgent

# Backwards compatibility bridges for existing tool/test scripts
from backend.app.agents.scheduling_agent import scheduling_agent

__all__ = [
    "ExecutiveSupervisorAgent",
    "MissionPlannerAgent",
    "TaskPlannerAgent",
    "DomainRouterAgent",
    "SchedulingDomainAgent",
    "EmailDomainAgent",
    "ResearchDomainAgent",
    "ExecutionVerifierAgent",
    "ExecutiveReporterAgent",
    "scheduling_agent"
]
