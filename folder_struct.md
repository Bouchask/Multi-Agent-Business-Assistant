This is how a **senior software engineer** would document the project. Every folder has **one responsibility**, clear **inputs**, **outputs**, and **dependencies**. This makes the project maintainable and easy to explain during your master's defense.

---

# Project Structure

```text
backend/
│
├── app/
│
├── api/
├── agents/
├── auth/
├── config/
├── core/
├── db/
├── graph/
├── llm/
├── middleware/
├── models/
├── prompts/
├── repositories/
├── schemas/
├── services/
├── tools/
├── utils/
│
├── main.py
```

---

# 1. api/

## Role

Expose REST APIs to the frontend.

The frontend **never talks directly** to agents or the database.

Everything passes through the API.

---

### Input

```text
HTTP Request

POST /chat

GET /projects

POST /login
```

---

### Output

```json
{
  "success": true,
  "data": {}
}
```

---

### Uses

* Services
* Schemas
* Auth
* LangGraph

---

### Doesn't know about

Database details.

---

Example

```text
Frontend

↓

POST /chat

↓

api/chat.py

↓

ChatService

↓

Supervisor Agent

↓

Response
```

---

# 2. agents/

## Role

Contains AI brains.

Each folder = one specialized AI.

---

Example

```text
agents/

supervisor/

research/

coding/

email/

calendar/

database/

memory/

report/

file/
```

---

Input

```python
Question

Conversation

Tools

Memory
```

---

Output

```python
AgentResponse

Selected Tool

Next Agent
```

---

Uses

* LLM
* Tools
* Memory
* Prompts

---

Doesn't know

Frontend

Database implementation

---

# Supervisor Agent

Input

```text
User Question
```

Output

```text
Choose Agent
```

Example

User

> Search AI news

↓

Research Agent

---

# Research Agent

Input

```text
Question
```

Uses

DuckDuckGo

Wikipedia

Calculator

Output

```text
Research Summary
```

---

# Report Agent

Input

```text
Business Data
```

Output

```text
PDF

Word

Excel
```

---

# Memory Agent

Input

```text
Conversation
```

Output

```text
Relevant Memory
```

---

# 3. auth/

## Role

Authentication.

Responsible only for users.

---

Input

```text
Email

Password
```

---

Output

```text
JWT Token
```

---

Contains

```text
jwt.py

security.py

permissions.py
```

---

Uses

Database

Password Hash

JWT

---

# 4. config/

## Role

Application configuration.

Nothing else.

---

Contains

```text
Settings

Environment

API Keys

URLs
```

---

Input

```text
.env
```

---

Output

```python
Config Object
```

---

Example

```python
settings.OPENROUTER_KEY
```

---

# 5. core/

## Role

Application core.

Global startup logic.

---

Contains

```text
Exceptions

Logging

Dependencies

Constants
```

---

Input

Application Start

---

Output

Initialized Application

---

# 6. db/

## Role

Everything related to database connection.

---

Contains

```text
engine.py

session.py

base.py
```

---

Input

SQL Query

---

Output

Database Session

---

Used by

Repositories

---

# 7. graph/

## Role

LangGraph workflow.

This is where all agents are connected.

---

Input

```text
Question
```

---

Output

```text
Final Answer
```

---

Contains

```text
nodes.py

edges.py

workflow.py
```

---

Example

```text
Supervisor

↓

Research

↓

Memory

↓

Report

↓

Supervisor

↓

Answer
```

---

# 8. llm/

## Role

Communicate with OpenRouter.

Only this folder knows the API.

---

Contains

```text
client.py

models.py

stream.py
```

---

Input

```python
Prompt
```

---

Output

```python
LLM Response
```

---

Uses

```text
OpenRouter
```

---

Nothing else calls OpenRouter directly.

---

# 9. middleware/

## Role

Runs before every request.

---

Example

```text
JWT Check

Logging

Rate Limit

CORS
```

---

Input

HTTP Request

---

Output

Modified Request

---

# 10. models/

## Role

SQLAlchemy Models.

Represents database tables.

---

Example

```python
User

Project

Meeting

Task
```

---

Input

Python Object

---

Output

Database Table

---

# 11. prompts/

## Role

Store AI prompts.

Never hardcode prompts.

---

Contains

```text
supervisor.txt

research.txt

email.txt
```

---

Input

Variables

---

Output

Prompt

---

Example

```text
You are a research assistant...
```

---

# 12. repositories/

## Role

Database layer.

Only this folder executes SQL.

---

Example

```text
UserRepository

TaskRepository

MeetingRepository
```

---

Input

Python Object

---

Output

Database Data

---

Uses

SQLAlchemy

---

# 13. schemas/

## Role

Validation.

Pydantic Models.

---

Input

JSON

---

Output

Python Object

---

Example

```python
LoginRequest

CreateProjectRequest

ChatRequest
```

---

# 14. services/

## Role

Business Logic.

Most important folder.

API should never contain logic.

---

Example

```text
ChatService

ProjectService

EmailService
```

---

Input

Validated Data

---

Output

Business Result

---

Uses

Repositories

Graph

LLM

---

Example

```text
API

↓

ChatService

↓

Supervisor

↓

Return
```

---

# 15. tools/

## Role

Functions AI can execute.

LLM never accesses APIs directly.

---

Example

```text
search.py

calculator.py

weather.py

github.py

gmail.py
```

---

Input

Arguments

---

Output

Real Data

---

Example

Question

↓

Research Agent

↓

Search Tool

↓

Google

↓

Result

↓

LLM

---

# 16. utils/

## Role

Reusable helper functions.

---

Example

```text
Date

PDF

File

JSON

Text

Logger
```

---

No business logic.

---

# main.py

Role

Application entry point.

Starts everything.

```python
app = FastAPI()
```

---

# Complete Data Flow

```text
User
 │
 ▼
Frontend (Next.js)
 │
 ▼
REST API (api/)
 │
 ▼
Pydantic Validation (schemas/)
 │
 ▼
Business Logic (services/)
 │
 ▼
LangGraph (graph/)
 │
 ▼
Supervisor Agent (agents/supervisor/)
 │
 ├───────────────┬──────────────────┬────────────────┐
 ▼               ▼                  ▼                ▼
Research      Database          Email          Report
Agent         Agent             Agent          Agent
 │               │                  │                │
 ▼               ▼                  ▼                ▼
Tools       Repository         Gmail API      ReportLab
 │               │
 ▼               ▼
DuckDuckGo   PostgreSQL
 │               │
 └──────┬────────┘
        ▼
Memory Agent
        │
        ▼
Qdrant
        │
        ▼
LLM (llm/)
        │
        ▼
Business Result
        │
        ▼
Service
        │
        ▼
API
        │
        ▼
Frontend
        │
        ▼
User
```

## 🔑 Golden Rule for the Architecture

Think of each layer as having **exactly one responsibility**:

| Folder            | Responsibility                 | Receives (Input)      | Returns (Output)              |
| ----------------- | ------------------------------ | --------------------- | ----------------------------- |
| **api/**          | Handle HTTP requests           | HTTP request          | JSON response                 |
| **schemas/**      | Validate data                  | JSON                  | Python objects                |
| **services/**     | Business logic                 | Validated data        | Business results              |
| **graph/**        | Orchestrate AI workflow        | User task             | Final agent result            |
| **agents/**       | AI reasoning                   | Task + context        | Decision or generated content |
| **tools/**        | Interact with external systems | Tool arguments        | Real-world data               |
| **repositories/** | Database access                | Queries/objects       | Database records              |
| **models/**       | Define database tables         | Python objects        | Database mappings             |
| **llm/**          | Talk to the language model     | Prompt/messages       | Model response                |
| **db/**           | Database connection            | Connection requests   | Database session              |
| **auth/**         | Authentication & authorization | Credentials/token     | User identity & permissions   |
| **config/**       | Application configuration      | Environment variables | Settings object               |
| **middleware/**   | Process requests globally      | HTTP request          | Modified request/response     |
| **utils/**        | Shared helper functions        | Various inputs        | Utility outputs               |
| **prompts/**      | AI instructions                | Variables             | Final prompt text             |

Following this separation makes the code easier to maintain, test, and extend, and it clearly demonstrates sound software architecture during your master's project presentation.
