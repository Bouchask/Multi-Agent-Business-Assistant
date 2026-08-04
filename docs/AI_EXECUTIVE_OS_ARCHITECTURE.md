# Enterprise AI Executive Operating System (Agentic AI OS)

## Architecture Overview

The **Autonomous Multi-Agent Business Assistant** has been fully refactored from a traditional chatbot into an enterprise-grade **Agentic AI Executive Operating System** inspired by OpenAI, Anthropic, LangGraph, CrewAI, AutoGen, and Google ADK.

```
                 USER
                   │
                   ▼
        Executive Supervisor (Governance & Strategic Routing)
                   │
                   ▼
          Mission Planner (Natural Language ➔ Structured Mission Schema)
                   │
                   ▼
            Task Planner (Granular Sequential / Parallel Task Breakdown)
                   │
                   ▼
           Domain Router (Zero-Execution Mapping to Domain AI)
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
 Scheduling     Email       Research
    Agent       Agent         Agent   (Reasoning ONLY; Zero Direct API Invocation)
      │            │            │
      ▼            ▼            ▼
 Calendar      Gmail API     Web Search  (Tool Layer: Strictly Structured JSON Output)
      │            │            │
      └────────────┼────────────┘
                   ▼
         Execution Verifier (Mandatory Independent Empirical DB & OAuth Audit)
                   │
                   ▼
        Executive Reporter (Clean Executive Markdown; Never Exposes JSON)
                   │
                   ▼
                  USER
```

---

## Explicit State Machine Lifecycle
Every corporate directive progresses through a strictly monitored, immutable state machine:
1. **`NEW`**: Directive ingested by Executive Supervisor.
2. **`PLANNED`**: Mission Planner structures domain targets, constraints, and dependencies.
3. **`TASKS_CREATED`**: Task Planner outputs granular operational task arrays.
4. **`ROUTED`**: Domain Router maps steps to specialized domain reasoning models.
5. **`EXECUTING`**: Domain Agents emit structured tool requests (evaluating Proactive Executive Confirmation protocols).
6. **`VERIFYING`**: Independent Execution Verifier checks SQLite storage records and live Google OAuth API link confirms.
7. **`COMPLETED`** or **`FAILED`**: Executive Reporter generates graceful conversational summaries based strictly on verified reality.

---

## Proactive Executive Secretary Core Protocol
- **Routine Low-Risk Tasks (`ROUTINE_SAFE`)**: Standard scheduling, open time booking, calendar querying, Date Libre overlapping conflict shifts, and routine notifications execute **autonomously without requesting confirmation**.
- **Sensitive Guardrails (`SENSITIVE_REQUIRES_CONFIRMATION`)**: Mass deletion across dates, destructive record replacements, or unauthorized sensitive changes are automatically intercepted by the domain reasoning engine to gently request executive authorization before any database or OAuth alteration occurs.

---

## Complete Module & Migration Map

| Old Monolithic Architecture | New Modular AI Executive OS Module | Primary Responsibility & Behavioral Mandate |
| :--- | :--- | :--- |
| `backend/app/agents/scheduling_agent.py` | `backend/app/workflows/engine.py` | Pure Python orchestration engine driving State Machine transitions & DI. |
| Mixed Chat Prompts | `backend/app/agents/supervisor/executive_supervisor.py` | Strategic goal analysis and workflow delegation. Zero tool calling. |
| String Matching Intents | `backend/app/agents/mission/mission_planner.py` | Converts text to structured Pydantic `StructuredMission` JSON schema. |
| Hardcoded Loop Checks | `backend/app/agents/planner/task_planner.py` | Granular sequential/parallel operational task breakdown. |
| If/Else Branching | `backend/app/agents/router/domain_router.py` | Dedicated domain selection routing (`SCHEDULING`, `EMAIL`, `RESEARCH`). |
| Injected Python Tool Calls | `backend/app/agents/domains/` | Domain reasoning ONLY; outputs `DomainExecutionRequest` JSON. |
| Raw API Returns | `backend/app/tools/` (`calendar/`, `gmail/`, etc.) | Tool Execution ONLY; returns structured dict/JSON without markdown. |
| Unverified Assumptions | `backend/app/agents/verification/execution_verifier.py` | Mandatory independent audit against persistent DB rows & OAuth APIs. |
| Raw Prompt Leakage | `backend/app/agents/reporting/executive_reporter.py` | Professional corporate markdown generator. |
| Raw History Scraping | `backend/app/memory/store.py` | Structured working memory objects isolating tasks, constraints & trust status. |
