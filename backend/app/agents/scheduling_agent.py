import json
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from backend.app.tools.calendar_tool import CalendarTool
from backend.app.llm.client import llm_client
from backend.app.llm.prompt_engineer import prompt_engineer

class SchedulingAgent:
    def run(self, instruction: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        logger.info(f"📅 SCHEDULING AGENT processing request: '{instruction}'")
        
        context_str = ""
        if history:
            last_msgs = history[-5:]
            context_str = "Recent Conversation Context:\n" + "\n".join([f"- {m.get('role', 'user')}: {m.get('content', '')}" for m in last_msgs]) + "\n\n"

        low_inst = instruction.lower().strip()
        
        # Step 1: Execute Prompt Engineer to convert keywords ("mots clés") into a Structured Mission Profile!
        is_explicit_query = any(pattern in low_inst for pattern in [
            "give programm", "give program", "show programm", "give calander", "show calander", 
            "give me calande", "list meeting", "programme meeting", "programme of meeting", "agenda of",
            "show detail"
        ]) and not any(verb in low_inst for verb in ["insert ", "add ", "book ", "create ", "schedule new", "auto programme", "auto program", "insert auto"])
        
        if is_explicit_query:
            month_filt = None
            m_match = re.search(r'month\s+(\d+)', low_inst)
            if m_match:
                month_filt = int(m_match.group(1))
            elif "august" in low_inst or "08/" in low_inst:
                month_filt = 8
            mission_profile = {
                "mission_title": "Schedule Inspection & Agenda Inquiry",
                "domain": "SCHEDULING",
                "action_type": "QUERY",
                "parameters": {"month_filter": month_filt},
                "execution_goals": ["Retrieve relational DB meetings", "Generate Google Calendar detail links"],
                "success_criteria": "Schedule presented clearly to executive user."
            }
        else:
            mission_profile = prompt_engineer.generate_mission_structure(raw_prompt=instruction, domain="SCHEDULING")
            
        action = mission_profile.get("action_type", "QUERY")
        params = mission_profile.get("parameters", {})
        
        # Format prompt engineer structure inside clean delimiters for native Streamlit Expander UI!
        goals_md = "\n".join([f"  - ✅ **{g}**" for g in mission_profile.get("execution_goals", ["Register schedule", "Sync with Google Calendar"])])
        mission_thinking = (
            f"---THINKING---\n"
            f"**Mission Objective**: `{mission_profile.get('mission_title', 'Execute Schedule Directive')}`  \n"
            f"**Domain Architecture**: `{mission_profile.get('domain', 'SCHEDULING')}`  \n"
            f"**Structured Parameters**: `{json.dumps(params)}`  \n"
            f"**Execution Goals**:  \n{goals_md}  \n"
            f"**Success Criteria**: *{mission_profile.get('success_criteria', 'Verified integration')}*  \n"
            f"---THINKING_END---\n\n"
        )

        # Step 2: Execute tool action (with Google Calendar auto-insert & conflict resolution)
        action_notice = ""
        gcal_link = ""
        if action in ["CREATE", "EXECUTE"] or any(w in low_inst for w in ["insert", "add", "book", "schedule"]):
            title = params.get("title", f"Meeting: {instruction[:30]}")
            date_val = params.get("date_str", params.get("date", "2026-08-24"))
            time_val = params.get("time_str", params.get("time", "10:00:00"))
            add_result = CalendarTool.add_meeting(title=str(title), date_str=str(date_val), time_str=str(time_val))
            
            if add_result.get("success"):
                gcal_link = add_result.get("google_calendar_link", "")
                is_api_synced = add_result.get("gcal_api_inserted", False)
                
                link_md = f"🔗 **[📅 Open, View & Save Details in Google Calendar]({gcal_link})**" if gcal_link else ""
                sync_bullet = f"\n- 🎉 **Gmail Auto-Sync**: *Successfully pushed directly to your primary Gmail account via OAuth API!*" if is_api_synced else ""
                
                if add_result.get("conflict_resolved"):
                    conf = add_result["conflict_details"]
                    action_notice = (
                        f"\n\n---\n"
                        f"#### 📋 Executive Scheduling Report\n"
                        f"- ⚠️ **Conflict Resolved**: Requested slot (**{conf['original_time']}**) was occupied by **'{conf['conflict_with']}'**.\n"
                        f"- ✨ **New Free Slot (*Date Libre*)**: Automatically registered **'{add_result['title']}'** at **{add_result['start']}**.\n"
                        f"- **Google Calendar Integration**: {link_md}{sync_bullet}"
                    )
                else:
                    action_notice = (
                        f"\n\n---\n"
                        f"#### 📋 Executive Scheduling Report\n"
                        f"- ⚡ **Status**: Successfully registered **'{add_result['title']}'** on **{add_result['start']}**.\n"
                        f"- **Google Calendar Integration**: {link_md}{sync_bullet}"
                    )
            else:
                action_notice = f"\n\n⚠️ Could not register DB meeting: {add_result.get('error')}"

        # Step 3: Fetch updated calendar events from DB & generate executive answer
        month_filt = params.get("month_filter")
        if not month_filt and ("month 8" in low_inst or "august" in low_inst):
            month_filt = 8
            
        calendar_data = CalendarTool.list_upcoming_meetings(filter_month=month_filt)
        events = calendar_data.get("events", [])
        events_formatted = []
        for e in events:
            loc = e.get("location_or_link", "Office")
            if str(loc).startswith("http") and "render?action=TEMPLATE" in str(loc):
                loc_str = f"([📅 Google Calendar Details]({loc}))"
            elif str(loc).startswith("http"):
                loc_str = f"([🔗 Web Access]({loc}))"
            else:
                loc_str = f"({loc})"
            end_str = e.get('end', '')
            time_range = f"{e.get('start', '')} - {end_str}" if end_str else f"{e.get('start', '')}"
            events_formatted.append(f"- **{time_range}**: {e.get('summary', 'Meeting')} {loc_str}")
            
        events_str = "\n".join(events_formatted) if events_formatted else "(No scheduled meetings found for this timeframe in database.)"
        
        system_instructions = (
            "You are an elite Executive Corporate Scheduling Assistant.\n"
            "Provide a concise, highly professional response directly to the user.\n"
            "CRITICAL DESIGN RULES:\n"
            "1. DO NOT output or repeat the Prompt Engineer Mission Profile or JSON schema in your response—that is already shown in the thinking block above!\n"
            "2. DO NOT duplicate links or notices if an Executive Scheduling Report is appended below.\n"
            "3. Speak cleanly, elegantly, and concisely without redundant boilerplate."
        )
        
        prompt = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": f"{context_str}User Directive: {instruction}\nAction Type: {action}\n\nLive Database Overview:\n{events_str}{action_notice}\n\nProvide a polite, crisp confirmation without repeating structural metadata."}
        ]
        res = llm_client.complete(messages=prompt)
        reply = res.get("content", "Schedule inspection completed.")
        
        # Assemble clean presentation: Thinking Box -> Concise Reply -> Stable Executive Report
        final_reply = mission_thinking + reply.strip()
        if action_notice and "Executive Scheduling Report" not in reply:
            final_reply += action_notice
            
        return final_reply

scheduling_agent = SchedulingAgent()
