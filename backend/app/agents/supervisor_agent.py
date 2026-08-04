from typing import Dict, Any, List, Optional
from loguru import logger
from backend.app.llm.client import llm_client

class SupervisorAgent:
    @staticmethod
    def route_request(user_input: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        context_str = ""
        if history:
            last_msgs = history[-3:]
            context_str = "Recent Conversation Context:\n" + "\n".join([f"- {m.get('role', 'user')}: {m.get('content', '')}" for m in last_msgs]) + "\n\n"

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are the Executive Supervisor Router for a Multi-Agent Business Assistant Operating System.\n"
                    "Classify the user request (considering recent conversation context) into exactly ONE of these specialized agent categories:\n"
                    "- RESEARCH: Competitor intelligence, market trends, web searches, news.\n"
                    "- EMAIL: Checking inbox, drafting messages, client correspondence.\n"
                    "- SCHEDULING: Checking calendar, dates, booking meetings, adding events, agenda syncs, confirming appointments.\n"
                    "- DEVELOPER: GitHub repositories, code inspections, programming questions, software issues.\n"
                    "- ANALYTICS: Database KPIs, project statistics, data charts, SQL queries.\n"
                    "- WRITER: Creating PDF or DOCX word reports, generating structured content docs.\n"
                    "- KNOWLEDGE: RAG queries, searching internal company manuals, vacation policy, rules.\n"
                    "- TRANSLATION: Translating content into French, Arabic, Spanish, or English.\n"
                    "- OCR_FILE: Reading PDFs, uploading documents, extracting OCR text from invoices/images.\n"
                    "- VISION_VOICE: Describing images, analyzing diagrams, speech-to-text or voice instructions.\n"
                    "- WORKFLOW: Automating repetitive tasks, pipeline event workflows, invoice automation.\n"
                    "- SECURITY: Checking audit logs, permissions, suspicious activity, role access.\n"
                    "- NOTIFICATION: Sending alerts, browser reminders, system notifications.\n"
                    "- GENERAL: Greetings, conversational chat, or general high-level help.\n\n"
                    "Respond ONLY with the exact category keyword in uppercase (e.g., SCHEDULING or RESEARCH)."
                )
            },
            {"role": "user", "content": f"{context_str}Current User Instruction: {user_input}"}
        ]
        res = llm_client.complete(messages=prompt, temperature=0.1)
        if not res.get("success"):
            return "GENERAL"
        reply = res.get("content", "").strip().upper()
        valid_categories = [
            "RESEARCH", "EMAIL", "SCHEDULING", "DEVELOPER", "ANALYTICS", "WRITER",
            "KNOWLEDGE", "TRANSLATION", "OCR_FILE", "VISION_VOICE", "WORKFLOW",
            "SECURITY", "NOTIFICATION", "GENERAL"
        ]
        for cat in valid_categories:
            if cat in reply:
                return cat
        return "GENERAL"

supervisor_agent = SupervisorAgent()
