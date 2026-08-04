import json
from typing import Dict, Any, Optional
from loguru import logger
from backend.app.llm.client import llm_client

class PromptEngineer:
    @staticmethod
    def generate_mission_structure(raw_prompt: str, domain: str = "SCHEDULING") -> Dict[str, Any]:
        """
        Transforms raw conversational instructions into a rigorous structured JSON Mission Profile,
        extracting all entities (like attendee email) and determining exact tool execution logic.
        """
        logger.info(f"🧠 PROMPT ENGINEER: Structuring mission for domain '{domain}' from raw input: '{raw_prompt}'")
        system_prompt = (
            "You are the Lead AI Prompt Engineer and System Architect for an Autonomous Executive OS.\n"
            "Your critical duty is to convert raw user instructions into an intelligent, structured JSON Mission Execution Profile.\n"
            "You must carefully identify all associated entities (e.g., attendee names, email addresses, notification requests) "
            "and define the precise function calls (required_tool_actions) that the downstream agents must execute.\n"
            "Do NOT return unstructured keywords. You MUST return valid JSON matching this exact schema:\n"
            "{\n"
            '  "mission_title": "Concise professional title of the task",\n'
            '  "domain": "' + domain.upper() + '",\n'
            '  "action_type": "CREATE or QUERY or EXECUTE",\n'
            '  "parameters": {\n'
            '    "title": "Clean event or task name (e.g. Meeting with Dr. Yahya for gestion labo)",\n'
            '    "date_str": "YYYY-MM-DD or descriptive date",\n'
            '    "time_str": "HH:MM:SS or 24h format (default to 10:00:00 if unspecified)",\n'
            '    "attendee_name": "Name of attendee or doctor if mentioned (e.g. Dr. Yahya), else null",\n'
            '    "attendee_email": "Email address if provided in prompt or inferred (e.g. dr.yahya@example.com), else null",\n'
            '    "location": "Location or meeting room if specified, else Corporate AI Office",\n'
            '    "month_filter": optional integer month for queries\n'
            '  },\n'
            '  "required_tool_actions": [\n'
            '    {\n'
            '      "tool": "CALENDAR_INSERT",\n'
            '      "enabled": true or false (true if booking/scheduling a meeting),\n'
            '      "reason": "Register meeting in database and sync with Google Calendar"\n'
            '    },\n'
            '    {\n'
            '      "tool": "GMAIL_SEND",\n'
            '      "enabled": true or false (SET TO TRUE IF ANY EMAIL ADDRESS IS MENTIONED OR IF USER ASKS TO NOTIFY/SEND MAIL),\n'
            '      "recipient": "Extracted email address or placeholder if missing",\n'
            '      "subject": "Formal meeting invitation subject",\n'
            '      "body": "Professional calendar invitation and summary message",\n'
            '      "reason": "Notify attendee via email with meeting details and link"\n'
            '    },\n'
            '    {\n'
            '      "tool": "DEMAND_CONFIRMATION",\n'
            '      "enabled": true or false (true ONLY if key parameters are severely ambiguous or user explicitly demands confirmation before execution),\n'
            '      "reason": "Verify details with executive before insertion"\n'
            '    }\n'
            '  ],\n'
            '  "execution_goals": ["Schedule the meeting", "Notify Dr. Yahya via email", "Confirm details"],\n'
            '  "success_criteria": "Meeting is successfully scheduled and confirmed with attendees"\n'
            "}\n"
            "Respond ONLY with the raw JSON object, nothing else."
        )
        
        try:
            res = llm_client.complete(messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Domain: {domain}\nRaw User Command: {raw_prompt}"}
            ], temperature=0.1)
            raw_json = res.get("content", "").strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:-3].strip()
            elif raw_json.startswith("```"):
                raw_json = raw_json[3:-3].strip()
                
            data = json.loads(raw_json)
            logger.info(f"✨ PROMPT ENGINEER STRUCTURED MISSION PROFILE:\n{json.dumps(data, indent=2)}")
            return data
        except Exception as e:
            logger.warning(f"Prompt Engineer structured parsing fallback: {e}")
            # Intelligent regex fallback for emails if LLM syntax parsing slips
            import re
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_prompt)
            found_email = email_match.group(0) if email_match else None
            return {
                "mission_title": f"Mission: {raw_prompt[:40]}",
                "domain": domain.upper(),
                "action_type": "CREATE" if any(w in raw_prompt.lower() for w in ["insert", "add", "book", "create", "schedule"]) else "QUERY",
                "parameters": {
                    "title": f"Meeting: {raw_prompt[:30]}", 
                    "date_str": "2026-08-24", 
                    "time_str": "10:00:00",
                    "attendee_email": found_email
                },
                "required_tool_actions": [
                    {"tool": "CALENDAR_INSERT", "enabled": True, "reason": "Schedule meeting"},
                    {"tool": "GMAIL_SEND", "enabled": bool(found_email), "recipient": found_email or "unknown", "subject": f"Meeting Invitation", "body": f"You are invited to {raw_prompt}", "reason": "Notify attendee via email"}
                ],
                "execution_goals": ["Execute schedule directive", f"Notify via email ({found_email})" if found_email else "Register calendar event"],
                "success_criteria": "Operation completed successfully and verified in database"
            }

    @staticmethod
    def optimize_and_expand(raw_prompt: str, domain: str = "general", add_detail_map: bool = True) -> str:
        """
        Legacy/General text expansion method to guarantee complete compatibility.
        """
        struct = PromptEngineer.generate_mission_structure(raw_prompt, domain=domain)
        return json.dumps(struct, indent=2)

prompt_engineer = PromptEngineer()
