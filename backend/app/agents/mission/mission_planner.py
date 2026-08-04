import json
import re
from typing import Dict, Any, List
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.models import StructuredMission, DomainType
from backend.app.core.state import MissionState, ExecutionMode
from backend.app.prompts import MISSION_PLANNER_PROMPT

class MissionPlannerAgent:
    """
    Agent 2: Mission Planner
    Responsibilities: Convert natural text into structured business mission JSON (objectives, intent, entities, filters, constraints).
    Strict Rule: Output only structured mission JSON. Never call tools. Single source of truth for execution & query filters.
    """
    @staticmethod
    def create_mission(user_prompt: str, supervisor_context: Dict[str, Any] = None) -> StructuredMission:
        logger.info(f"💼 MISSION PLANNER: Structuring mission from input: '{user_prompt}'")
        
        # Helper: Deterministic natural language filter enhancer to ensure 100% parameter preservation
        def extract_deterministic_filters(text: str, current_filters: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
            filters = dict(current_filters)
            # Mirror filter keywords from entities if not explicitly in filters
            filter_keys = [
                "participant", "participants", "email", "date", "month", "year", 
                "start_date", "end_date", "title", "keyword", "location", "status", 
                "source", "limit", "sort"
            ]
            for k in filter_keys:
                if k in entities and k not in filters:
                    filters[k] = entities[k]
                    
            low = text.lower()
            
            # Participant extraction (e.g. "with Ayoub", "with Dr. Yahya")
            if "participant" not in filters and "participants" not in filters:
                with_match = re.search(r'\bwith\s+([a-z0-9\.\s-]+?)(?:\s+(?:in|on|during|for|at|from|to|today|tomorrow|next|this|by|only)|\s*$)', text, re.IGNORECASE)
                if with_match:
                    p_name = with_match.group(1).strip()
                    if p_name and not any(w in p_name.lower() for w in ["email", "gmail", "yahoo"]):
                        filters["participant"] = p_name
            
            # Month extraction (e.g. "in August", "during August 2026", "this month")
            month_names = {
                "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
                "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
                "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
            }
            if "month" not in filters:
                for m_str, m_num in month_names.items():
                    if re.search(rf'\b(in|during|for|on)?\s*{m_str}\b', low):
                        filters["month"] = m_num
                        break
                if "this month" in low or "current month" in low or "in this. month" in low:
                    import datetime
                    filters["month"] = datetime.datetime.now().month
                    
            # Date extraction (e.g. "August 24", "24-08-2026", "2026-08-24")
            if "date" not in filters:
                date_match = re.search(r'\b(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}|\d{1,2}\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{1,2})\b', low, re.IGNORECASE)
                if date_match:
                    filters["date"] = date_match.group(1).strip()
                    
            # Year extraction
            if "year" not in filters:
                year_match = re.search(r'\b(202[0-9])\b', low)
                if year_match:
                    filters["year"] = int(year_match.group(1))
                    
            # Calendar Source selection
            if "source" not in filters:
                if any(w in low for w in ["database only", "local database only", "local db only", "db only"]):
                    filters["source"] = "database"
                elif any(w in low for w in ["google calendar only", "google only", "gcal only"]):
                    filters["source"] = "google_calendar"

            # Status filtering
            if "status" not in filters:
                if "upcoming" in low:
                    filters["status"] = "upcoming"
                elif "completed" in low or "past" in low:
                    filters["status"] = "completed"

            # Clean empty filters
            return {k: v for k, v in filters.items() if v is not None and v != "" and v != []}

        try:
            res = llm_client.complete(
                messages=[
                    {"role": "system", "content": MISSION_PLANNER_PROMPT},
                    {"role": "user", "content": f"User Request: '{user_prompt}'\nSupervisor Context: {json.dumps(supervisor_context or {})}"}
                ],
                temperature=0.1
            )
            raw = res.get("content", "{}").strip()
            if raw.startswith("```json"):
                raw = raw[7:-3].strip()
            elif raw.startswith("```"):
                raw = raw[3:-3].strip()
            data = json.loads(raw)
            logger.info(f"✨ MISSION PLANNER SCHEMA: {data}")
            
            domains = [DomainType(d) for d in data.get("required_domains", ["SCHEDULING"]) if d in DomainType.__members__]
            if not domains:
                domains = [DomainType.SCHEDULING]
                
            entities = data.get("entities", {})
            raw_filters = data.get("filters", {})
            filters = extract_deterministic_filters(user_prompt, raw_filters, entities)
            
            logger.info(f"✨ MISSION PLANNER FILTERS PRESERVED: {json.dumps(filters)}")
                
            return StructuredMission(
                raw_input=user_prompt,
                objective=data.get("objective", f"Execute directive for '{user_prompt[:30]}'"),
                intent=data.get("intent", "EXECUTE"),
                entities=entities,
                filters=filters,
                constraints=data.get("constraints", ["Prevent double-booking", "Require authorization for destructive actions"]),
                dependencies=data.get("dependencies", ["Check existing calendar records"]),
                required_domains=domains,
                execution_mode=ExecutionMode.SEQUENTIAL,
                state=MissionState.PLANNED
            )
        except Exception as e:
            logger.warning(f"Mission Planner parsing fallback: {e}")
            low = user_prompt.lower()
            if any(w in low for w in ["delete", "supprime", "cancel", "clear", "remove"]):
                intent = "DELETE"
            elif any(w in low for w in ["insert", "add", "book", "schedule", "create"]):
                intent = "CREATE"
            elif any(w in low for w in ["list", "query", "show", "find", "give me list", "agenda", "meetings"]):
                intent = "QUERY_MEETINGS"
            else:
                intent = "QUERY"

            emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', user_prompt)
            entities = {"title": user_prompt[:35], "emails": emails}
            filters = extract_deterministic_filters(user_prompt, {}, entities)
            
            logger.info(f"✨ FALLBACK FILTERS PRESERVED: {json.dumps(filters)}")
            return StructuredMission(
                raw_input=user_prompt,
                objective=f"Process {intent} directive for user request",
                intent=intent,
                entities=entities,
                filters=filters,
                required_domains=[DomainType.SCHEDULING, DomainType.EMAIL] if emails else [DomainType.SCHEDULING],
                state=MissionState.PLANNED
            )
