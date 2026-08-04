# 🌐 API, Service & Infrastructure Requirements

This document outlines the complete list of external APIs, artificial intelligence services, SDKs, and infrastructure dependencies required to develop and deploy the **Multi-Agent Business Assistant** across all 20 agents and developmental phases.

---

## 1. 🤖 AI Models, LLMs & Vector Infrastructure

| Service / API Name | Purpose in Project | Recommended Provider / Tier | Required Auth / Config |
| :--- | :--- | :--- | :--- |
| **OpenRouter API** | **Core LLM Reasoning**: Powers the Supervisor, Research, Coding, Analytics, and SQL agents by dynamically routing to optimal models (Claude 3.5 Sonnet, GPT-4o, Gemini Pro, Llama 3, DeepSeek). | **OpenRouter.ai** (Pay-as-you-go, no monthly subscription needed) | `OPENROUTER_API_KEY`<br>`OPENROUTER_BASE_URL` |
| **Embeddings API / Model** | Transforms uploaded company documents (RAG) and conversational memory into vector embeddings for semantic similarity search. | **Option A (Free & Local):** `FastEmbed` / BAAI `bge-m3` model.<br>**Option B (Cloud API):** OpenAI `text-embedding-3-small`. | Local library or `EMBEDDING_API_KEY` |
| **Qdrant Vector DB** | **Knowledge Base & Memory Store**: Indexes document chunks (RAG) and long-term user & conversation memories. | **Option A (Free Dev):** Local Qdrant Container via Docker.<br>**Option B (Prod):** Qdrant Cloud (Free Tier available). | `QDRANT_HOST`<br>`QDRANT_API_KEY` (if cloud) |

---

## 2. 📧 Email, Calendar & Communication APIs

> [!IMPORTANT]
> Requires creating a dedicated project in the **Google Cloud Console** and enabling the Gmail API and Google Calendar API with OAuth 2.0 Client Credentials.

| Service / API Name | Purpose in Project | Recommended Provider / Tier | Required Auth / Config |
| :--- | :--- | :--- | :--- |
| **Google Calendar API** | **Calendar Agent (#5)**: Checking employee schedules, finding available meeting slots, scheduling meetings, and sending RSVP invitations. | **Google Cloud Console** (Free API Tier) | `GOOGLE_CLIENT_ID`<br>`GOOGLE_CLIENT_SECRET`<br>`GOOGLE_REFRESH_TOKEN` |
| **Gmail API** | **Email Agent (#4)**: Reading company inboxes, classifying incoming emails, drafting replies, and sending outgoing messages. | **Google Cloud Console** (Free API Tier) | *Uses same Google OAuth2 Token as Calendar* |
| **Resend / SendGrid API** | **Notification Agent (#10) & Auth (#3)**: Sending automated transactional system emails (password resets, login security alerts, PDF reports). | **Resend.com** (Free tier: 3,000 emails/month) or **SendGrid** | `RESEND_API_KEY` or SMTP credentials |

---

## 3. 🔍 Web Research & External Data APIs

| Service / API Name | Purpose in Project | Recommended Provider / Tier | Required Auth / Config |
| :--- | :--- | :--- | :--- |
| **DuckDuckGo Search** | **Research Agent (#2)**: Real-time internet searches for competitor analysis, general web research, and live news parsing. | **`duckduckgo-search` Python SDK** (100% Free, no rate limit restrictions) | None (Local Python library) |
| **Tavily AI Search / Serper.dev** *(Optional)* | Advanced, AI-native web search API that extracts clean markdown content from web pages instead of RAW HTML tags. | **Tavily AI** (Free tier: 1,000 searches/month) or **SerpAPI** | `TAVILY_API_KEY` or `SERPER_API_KEY` |
| **Wikipedia API** | **Research Agent (#2)**: Querying encyclopedic definitions, industry terminologies, and company background overviews. | **`wikipedia` Python SDK** (100% Free) | None (Local Python library) |
| **GitHub API** *(Optional)* | **Coding Agent (#3)**: Allowing the developer assistant to read codebase repositories, analyze commits, or review pull requests. | **GitHub REST / GraphQL API** (Free) | `GITHUB_PERSONAL_ACCESS_TOKEN` |

---

## 4. 📄 Document Processing, OCR & Vision APIs

| Service / API Name | Purpose in Project | Recommended Provider / Tier | Required Auth / Config |
| :--- | :--- | :--- | :--- |
| **Vision LLM API** | **Vision Agent (#17) & OCR Agent (#16)**: Analyzing visual diagrams, deciphering complex charts, and extracting structured JSON data from scanned invoices. | **OpenAI GPT-4o Vision** or **Claude 3.5 Sonnet Vision** (Accessed directly via your existing **OpenRouter API Key**) | *Uses OpenRouter API Key* |
| **Local OCR Engine** | **File Agent (#9) & OCR Agent (#16)**: Extracting raw text from uploaded images or scanned PDF documents without spending cloud tokens. | **Tesseract OCR** (via `pytesseract` in Docker) or **EasyOCR / PyMuPDF** | Installed natively inside backend Dockerfile |
| **Report Generators** | **Report Agent (#6)**: Generating enterprise presentations, analytics spreadsheets, Word manuals, and PDF meeting briefs. | **Python Standard Libraries (100% Free):**<br>• `ReportLab` or `WeasyPrint` (PDF)<br>• `python-docx` (Word DOCX)<br>• `openpyxl` / `pandas` (Excel XLSX)<br>• `python-pptx` (PowerPoint PPTX) | None (Local Python package dependencies) |

---

## 5. 🎤 Voice & Multilingual Translation APIs

| Service / API Name | Purpose in Project | Recommended Provider / Tier | Required Auth / Config |
| :--- | :--- | :--- | :--- |
| **Speech-to-Text (STT)** | **Voice Agent (#18)**: Converting spoken commands or recorded meeting audio into text prompts for the Supervisor Agent. | **Option A (Free & Local):** `faster-whisper` Python open-source model.<br>**Option B (Cloud API):** OpenAI Whisper API (via OpenRouter/OpenAI). | Local AI model or `OPENAI_API_KEY` |
| **Text-to-Speech (TTS)** | **Voice Agent (#18)**: Generating vocal summaries or voice responses from the AI Assistant. | **Option A (Free & Offline):** **Piper TTS** (Fast, lightweight local voice engine).<br>**Option B (Cloud API):** ElevenLabs API or OpenAI TTS. | Installed in Docker or `ELEVENLABS_API_KEY` |
| **Translation Engine** | **Translation Agent (#15)**: Translating reports and documents between English, French, Arabic, and Spanish. | Powered natively by **OpenRouter LLMs** (Models like Claude 3.5 Sonnet and Gemini Pro outperform legacy APIs in Nuance, Arabic formatting, and Business idioms). | *Uses OpenRouter API Key* |

---

## 6. 🛠️ Core Infrastructure & DevOps Requirements

| Component | Purpose in Project | Recommended Setup / Providers | Configuration Required |
| :--- | :--- | :--- | :--- |
| **PostgreSQL Database** | Primary relational SQL datastore for Users, Roles, Tasks, Projects, Meetings, and system audit logs. | **Development:** Local Docker Container.<br>**Production:** Neon.tech, Supabase, or Railway (Free tiers available). | `DATABASE_URL=` (Postgres connection string) |
| **Redis Instance** | High-speed memory cache for JWT token revocation, AI token budget rate-limiting, WebSocket Realtime Pub/Sub, and Celery worker queues. | **Development:** Local Docker Container.<br>**Production:** Upstash or Railway Redis. | `REDIS_URL=` |
| **Object Storage (S3)** | Persistent storage for uploaded PDF documents, Excel sheets, user avatars, and generated report files. | **Option A (Free Dev):** Local file directory volume in Docker.<br>**Option B (Prod):** Cloudflare R2 or AWS S3 (R2 has zero egress fees). | `S3_BUCKET_NAME`<br>`S3_ACCESS_KEY`<br>`S3_SECRET_KEY` |
| **Container & Hosting** | Deployment environments for frontend (Next.js) and backend backend container services. | **Vercel** (Frontend) + **Render / Railway / Docker** (Backend API & Background workers). | Deployment Webhooks & GitHub Actions CI/CD Secrets |

---

## 7. 📋 Environment Variables Template (`.env.example`)

Below is the complete architectural configuration template needed for **Phase 2 (Environment Setup)**:

```bash
# =====================================================================
# --- APPLICATION CORE SETTINGS ---
# =====================================================================
APP_ENV="development"
API_PORT=8000
FRONTEND_URL="http://localhost:3000"
SECRET_KEY="replace-with-secure-32-character-random-secret"
ACCESS_TOKEN_EXPIRE_MINUTES=60
LOG_LEVEL="INFO"

# =====================================================================
# --- DATABASE & VECTOR STORAGE ---
# =====================================================================
DATABASE_URL="postgresql://postgres:password@localhost:5432/business_assistant"
REDIS_URL="redis://localhost:6379/0"
QDRANT_HOST="http://localhost:6333"
# QDRANT_API_KEY="" # Required only for cloud Qdrant instances

# =====================================================================
# --- AI & LLM MODEL ORCHESTRATION (OpenRouter) ---
# =====================================================================
OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL="anthropic/claude-3.5-sonnet"
OPENROUTER_FAST_MODEL="google/gemini-pro-1.5"
OPENROUTER_CODING_MODEL="deepseek/deepseek-coder"
EMBEDDING_MODEL="BAAI/bge-m3"  # Or 'text-embedding-3-small' for OpenAI cloud

# =====================================================================
# --- GOOGLE WORKSPACE INTEGRATIONS (Calendar & Email) ---
# =====================================================================
GOOGLE_CLIENT_ID="xxxxxxxxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="xxxxx-xxxxxxxxxxxxxxxxxxxxx"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/v1/auth/google/callback"

# =====================================================================
# --- SYSTEM NOTIFICATIONS & TRANSACTIONAL SMTP ---
# =====================================================================
SMTP_HOST="smtp.resend.com"
SMTP_PORT=465
SMTP_USER="resend"
SMTP_PASSWORD="re_xxxxxxxxxxxxxxxxxxx"
SENDER_EMAIL="notifications@yourcompany.com"

# =====================================================================
# --- OPTIONAL AI EXTENSIONS & INTEGRATIONS ---
# =====================================================================
TAVILY_API_KEY="tvly-xxxxxxxxxxxxxxx"            # For advanced AI web research & scraping
GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxxxxxxxxxxxx"  # For developer coding agent repository inspection
ELEVENLABS_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxx"     # Optional for Voice TTS responses
```
