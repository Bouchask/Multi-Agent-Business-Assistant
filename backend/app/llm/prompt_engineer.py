import json
import re
from typing import Dict, Any, Optional
from loguru import logger
from backend.app.llm.client import llm_client

class PromptEngineer:
    @staticmethod
    def generate_mission_structure(raw_prompt: str, domain: str = "SCHEDULING") -> Dict[str, Any]:
        """
        Transforms raw conversational instructions into an autonomous executive mission profile.
        If domain is SCHEDULING, invokes the elite Executive Scheduling Mission Planner schema.
        """
        logger.info(f"🧠 PROMPT ENGINEER: Structuring mission for domain '{domain}' from raw input: '{raw_prompt}'")
        
        if domain.upper() == "SCHEDULING":
            system_prompt = (
                "You are the Executive Scheduling Mission Planner.\n\n"
                "Your responsibility is NOT to answer the user.\n\n"
                "Your responsibility is to transform the user's request into an autonomous mission.\n\n"
                "You must understand intent exactly like an executive assistant.\n\n"
                "You must determine:\n"
                "• Is the user asking to create a meeting?\n"
                "• Query meetings?\n"
                "• Modify a meeting?\n"
                "• Delete a meeting?\n"
                "• Ask about availability?\n"
                "• Confirm a previous pending action?\n\n"
                "Never invent information.\n\n"
                "Return ONLY valid JSON matching this schema:\n"
                "{\n"
                '  "mission": "CREATE | UPDATE | DELETE | QUERY | CONFIRM | CANCEL",\n'
                '  "requires_calendar_lookup": true,\n'
                '  "requires_duplicate_check": true,\n'
                '  "requires_conflict_check": true,\n'
                '  "requires_confirmation": false,\n'
                '  "priority": "LOW | NORMAL | HIGH",\n'
                '  "entities": {\n'
                '      "title": "",\n'
                '      "participants": [],\n'
                '      "emails": [],\n'
                '      "date": "",\n'
                '      "time": "",\n'
                '      "duration": "60",\n'
                '      "location": "",\n'
                '      "description": ""\n'
                '  },\n'
                '  "reasoning": [\n'
                '      "...",\n'
                '      "..."\n'
                '  ]\n'
                "}\n"
                "Respond ONLY with the raw JSON object, nothing else."
            )
        else:
            system_prompt = (
                "You are the Lead AI Prompt Engineer and System Architect for an Autonomous Executive OS.\n"
                "Your critical duty is to convert raw user instructions into a rigorous, structured JSON Mission Execution Profile.\n"
                "Do NOT return unstructured keywords. You MUST return valid JSON matching this exact schema:\n"
                "{\n"
                '  "mission": "CREATE or QUERY or EXECUTE",\n'
                '  "domain": "' + domain.upper() + '",\n'
                '  "priority": "NORMAL",\n'
                '  "entities": {"title": "Task name", "date": "2026-08-24", "time": "10:00:00"},\n'
                '  "reasoning": ["Analyze user goal", "Execute specialized domain tools"]\n'
                "}\n"
                "Respond ONLY with the raw JSON object, nothing else."
            )
        
        try:
            res = llm_client.complete(messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Command: {raw_prompt}"}
            ], temperature=0.1)
            raw_json = res.get("content", "").strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:-3].strip()
            elif raw_json.startswith("```"):
                raw_json = raw_json[3:-3].strip()
                
            data = json.loads(raw_json)
            logger.info(f"✨ EXECUTIVE MISSION PLANNER OUTPUT:\n{json.dumps(data, indent=2)}")
            return data
        except Exception as e:
            logger.warning(f"Executive Mission Planner fallback: {e}")
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_prompt)
            found_email = [email_match.group(0)] if email_match else []
            is_create = any(w in raw_prompt.lower() for w in ["insert", "add", "book", "create", "schedule"])
            return {
                "mission": "CREATE" if is_create else "QUERY",
                "requires_calendar_lookup": True,
                "requires_duplicate_check": is_create,
                "requires_conflict_check": is_create,
                "requires_confirmation": False,
                "priority": "NORMAL",
                "entities": {
                    "title": f"Meeting: {raw_prompt[:30]}", 
                    "participants": ["Colleague"],
                    "emails": found_email,
                    "date": "2026-08-24", 
                    "time": "10:00:00",
                    "duration": "60",
                    "location": "Corporate Office",
                    "description": raw_prompt
                },
                "reasoning": ["Extracted schedule goal from user command", "Defaulted to standard priority and verification flags"]
            }

    @staticmethod
    def optimize_and_expand(raw_prompt: str, domain: str = "general", add_detail_map: bool = True) -> str:
        struct = PromptEngineer.generate_mission_structure(raw_prompt, domain=domain)
        return json.dumps(struct, indent=2)

prompt_engineer = PromptEngineer()
