import json
from typing import Dict, Any, Optional
from loguru import logger
from backend.app.llm.client import llm_client

class PromptEngineer:
    @staticmethod
    def generate_mission_structure(raw_prompt: str, domain: str = "SCHEDULING") -> Dict[str, Any]:
        """
        Transforms raw conversational instruction (words/keywords) into a formal, 
        structured JSON Mission Profile with explicit parameters and execution goals.
        """
        logger.info(f"🧠 PROMPT ENGINEER: Structuring mission for domain '{domain}' from raw input: '{raw_prompt}'")
        system_prompt = (
            "You are the Lead AI Prompt Engineer and System Architect.\n"
            "Your critical job is to convert raw, unstructured user instructions (simple keywords / 'mots clés') "
            "into a rigorous, structured JSON Mission Execution Profile ('struct for mission').\n"
            "Do NOT return unstructured keywords. You MUST return valid JSON matching this schema:\n"
            "{\n"
            '  "mission_title": "Concise professional title of the task",\n'
            '  "domain": "' + domain.upper() + '",\n'
            '  "action_type": "CREATE or QUERY or EXECUTE",\n'
            '  "parameters": {\n'
            '    "title": "Clean event or task name",\n'
            '    "date_str": "YYYY-MM-DD or descriptive date",\n'
            '    "time_str": "HH:MM AM/PM or 24h format (default to 10:00:00 if unspecified)",\n'
            '    "month_filter": optional integer month for queries\n'
            '  },\n'
            '  "execution_goals": ["Goal 1", "Goal 2", "Goal 3"],\n'
            '  "success_criteria": "Clear definition of success"\n'
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
                raw_json = raw_json.replace("```json", "").replace("```", "").strip()
            elif raw_json.startswith("```"):
                raw_json = raw_json.replace("```", "").strip()
                
            data = json.loads(raw_json)
            logger.info(f"✨ PROMPT ENGINEER STRUCTURED MISSION PROFILE:\n{json.dumps(data, indent=2)}")
            return data
        except Exception as e:
            logger.warning(f"Prompt Engineer structured parsing fallback: {e}")
            return {
                "mission_title": f"Mission: {raw_prompt[:40]}",
                "domain": domain.upper(),
                "action_type": "CREATE" if any(w in raw_prompt.lower() for w in ["insert", "add", "book", "create", "schedule"]) else "QUERY",
                "parameters": {"title": f"Meeting: {raw_prompt[:30]}", "date_str": "2026-08-24", "time_str": "10:00:00"},
                "execution_goals": ["Execute instruction", "Verify results in database"],
                "success_criteria": "Operation completed successfully"
            }

    @staticmethod
    def optimize_and_expand(raw_prompt: str, domain: str = "general", add_detail_map: bool = True) -> str:
        """
        Legacy/General text expansion method to guarantee complete compatibility.
        """
        struct = PromptEngineer.generate_mission_structure(raw_prompt, domain=domain)
        return json.dumps(struct, indent=2)

prompt_engineer = PromptEngineer()
