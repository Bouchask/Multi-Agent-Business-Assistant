import json
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from backend.app.tools.calendar_tool import CalendarTool
from backend.app.tools.gmail_tool import GmailTool
from backend.app.llm.client import llm_client
from backend.app.llm.prompt_engineer import prompt_engineer

class SchedulingAgent:
    def _evaluate_semantic_duplication(self, title: str, date_str: str, time_str: str, events: List[Dict[str, Any]], user_prompt: str) -> Dict[str, Any]:
        """
        Uses LLM intelligence to evaluate if a requested meeting is a genuine duplicate on the same date,
        returning natural conversational guidance instead of rigid boilerplate templates.
        """
        override_words = ["confirm", "force", "insert anyway", "oui", "yes proceed", "ignore warning", "override", "valide", "valider", "yes"]
        if any(w in user_prompt.lower() for w in override_words):
            return {"conflict_detected": False, "reasoning": "User provided explicit authorization override."}

        if not events:
            return {"conflict_detected": False, "reasoning": "No existing calendar events found."}

        same_date_events = [e for e in events if date_str in str(e.get("start", ""))]
        
        if not same_date_events:
            return {"conflict_detected": False, "reasoning": f"No existing events found on {date_str}. Meetings on different dates are distinct sessions."}

        eval_prompt = [
            {
                "role": "system",
                "content": (
                    "You are an elite, natural Executive Corporate Assistant and Calendar Auditor.\n"
                    "Your job is to check if a newly requested meeting on a specific date is an accidental duplicate of an already scheduled meeting ON THE SAME DATE.\n"
                    "CRITICAL INTELLIGENT RULE:\n"
                    "- Only flag as a duplicate/error if there is an existing meeting with the same person or subject on the EXACT SAME DATE around the same time or if scheduling twice in the same morning/afternoon appears accidental.\n"
                    "- Never treat meetings on different dates or different weeks as duplicates!\n\n"
                    "Respond STRICTLY with a valid JSON object matching this schema:\n"
                    "{\n"
                    "  \"conflict_detected\": true/false,\n"
                    "  \"reasoning\": \"Brief thought process behind your determination\",\n"
                    "  \"conversational_message\": \"If conflict_detected is true, write a natural, polite, helpful message directly to the user explaining that you noticed they already have a meeting with this person at that time/day, and gently ask if they want to schedule an additional session or if it was a duplicate. Keep it conversational like ChatGPT or a smart human assistant—NO robotic headers, NO boilerplate formulas, NO 'Action Required' checklists.\"\n"
                    "}\n"
                )
            },
            {
                "role": "user",
                "content": f"New Meeting Request:\nTitle: {title}\nDate: {date_str}\nTime: {time_str}\n\nExisting Events on this same date ({date_str}):\n{json.dumps(same_date_events, indent=2)}\n\nEvaluate for semantic deduplication on this exact date."
            }
        ]
        
        try:
            res = llm_client.complete(messages=eval_prompt)
            content = res.get("content", "{}").strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            data = json.loads(content)
            logger.info(f"🧠 Semantic Deduplication Audit Result: {data}")
            return data
        except Exception as e:
            logger.warning(f"Semantic audit error: {e}. Defaulting to safe proceed.")
            return {"conflict_detected": False}

    def run(self, instruction: str, history: Optional[List[Dict[str, Any]]] = None) -> str:
        logger.info(f"📅 SCHEDULING AGENT processing request: '{instruction}'")
        
        context_str = ""
        if history:
            last_msgs = history[-5:]
            context_str = "Recent Conversation Context:\n" + "\n".join([f"- {m.get('role', 'user')}: {m.get('content', '')}" for m in last_msgs]) + "\n\n"

        low_inst = instruction.lower().strip()
        
        # Step 1: Execute Executive Scheduling Mission Planner
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
                "mission": "QUERY",
                "requires_calendar_lookup": True,
                "requires_duplicate_check": False,
                "requires_conflict_check": False,
                "priority": "NORMAL",
                "entities": {"date": f"Month {month_filt}" if month_filt else "All"},
                "reasoning": ["Executive user requested schedule overview and agenda details"]
            }
        else:
            mission_profile = prompt_engineer.generate_mission_structure(raw_prompt=instruction, domain="SCHEDULING")
            
        mission = mission_profile.get("mission", mission_profile.get("action_type", "QUERY"))
        entities = mission_profile.get("entities", mission_profile.get("parameters", {}))
        reasoning_list = mission_profile.get("reasoning", ["Analyze executive command", "Execute domain workflow"])
        
        # Format Executive Mission Planner structure inside clean delimiters for ChatGPT Reasoning Dropdown!
        reason_md = "\n".join([f"  - 💭 *{r}*" for r in reasoning_list if r])
        participants = entities.get("participants", [])
        emails = entities.get("emails", [])
        if isinstance(participants, list):
            part_str = ", ".join(participants) if participants else "None specified"
        else:
            part_str = str(participants)
            
        if isinstance(emails, list):
            email_str = ", ".join(emails) if emails else (entities.get("attendee_email") or "None specified")
        else:
            email_str = str(emails)

        mission_thinking = (
            f"---THINKING---\n"
            f"**Mission Directive**: `[{mission}]` | **Priority**: `{mission_profile.get('priority', 'NORMAL')}`  \n"
            f"**Executive Reasoning**:  \n{reason_md}  \n"
            f"**Extracted Entities**:  \n"
            f"  - **Title**: `{entities.get('title', 'Meeting')}`  \n"
            f"  - **Participants**: `{part_str}`  \n"
            f"  - **Emails**: `{email_str}`  \n"
            f"  - **Date & Time**: `{entities.get('date', entities.get('date_str', '2026-08-24'))} @ {entities.get('time', entities.get('time_str', '10:00:00'))}` (Duration: `{entities.get('duration', '60')}m`)  \n"
            f"**Autonomous Flags**: `[Lookup: {mission_profile.get('requires_calendar_lookup', True)}] [Dup-Check: {mission_profile.get('requires_duplicate_check', True)}] [Conflict: {mission_profile.get('requires_conflict_check', True)}]`  \n"
            f"---THINKING_END---\n\n"
        )

        # Check if planner demands confirmation before executing action
        if mission_profile.get("requires_confirmation", False) and not any(w in low_inst for w in ["confirm", "oui", "valide", "proceed", "yes"]):
            logger.info("⚡ Executive Mission Planner requested preliminary verification.")
            verify_msg = (
                f"Before I finalize this event and send out notifications, could you please confirm if you would like me to schedule `{entities.get('title')}` on `{entities.get('date', 'specified date')}` at `{entities.get('time', 'specified time')}`? Simply reply 'yes' or 'confirm' to execute."
            )
            return mission_thinking + verify_msg

        # Step 2: Execute tool action
        action_notice = ""
        gcal_link = ""
        email_notice = ""
        
        should_insert = mission in ["CREATE", "UPDATE", "CONFIRM"] or any(w in low_inst for w in ["insert", "add", "book", "schedule"])
        
        if should_insert:
            title = entities.get("title", f"Meeting: {instruction[:30]}")
            date_val = entities.get("date", entities.get("date_str", "2026-08-24"))
            time_val = entities.get("time", entities.get("time_str", "10:00:00"))

            # --- LLM INTELLIGENT DEDUPLICATION AUDIT ---
            if mission_profile.get("requires_duplicate_check", True):
                all_existing = CalendarTool.list_upcoming_meetings(filter_month=None).get("events", [])
                audit_res = self._evaluate_semantic_duplication(str(title), str(date_val), str(time_val), all_existing, instruction)
                
                if audit_res.get("conflict_detected") and not any(w in low_inst for w in ["confirm", "force", "valide", "yes"]):
                    logger.warning(f"🛡️ Intercepted genuine same-day schedule conflict for '{title}' on {date_val}.")
                    
                    dedup_thinking = (
                        f"---THINKING---\n"
                        f"**Mission Directive**: `[DEDUPLICATION_AUDIT]` | **Priority**: `HIGH`  \n"
                        f"**Executive Reasoning**:  \n"
                        f"  - 💭 *Detected existing event on exact same date ({date_val})*  \n"
                        f"  - 💭 *Intercepting insertion to prevent calendar double-booking*  \n"
                        f"**Autonomous Flags**: `[Dup-Check: CONFLICT_DETECTED]`  \n"
                        f"---THINKING_END---\n\n"
                    )
                    
                    conversational_reply = audit_res.get(
                        "conversational_message", 
                        f"I noticed you already have a meeting scheduled with Dr. Yahya on {date_val} around that time. Would you like me to book this as an additional session on that day, or should we update the existing one?"
                    )
                    
                    return dedup_thinking + conversational_reply

            # Proceed with DB registration & Google Calendar API insertion
            add_result = CalendarTool.add_meeting(title=str(title), date_str=str(date_val), time_str=str(time_val))
            
            # --- EXECUTE GMAIL NOTIFICATION ---
            recipients = entities.get("emails", [])
            if not recipients and entities.get("attendee_email"):
                recipients = [entities.get("attendee_email")]
            elif not recipients:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', instruction)
                if email_match:
                    recipients = [email_match.group(0)]
            
            if recipients:
                for recipient in recipients:
                    subj = f"Meeting Invitation & Confirmation: {add_result.get('title', title)}"
                    body_html = (
                        f"<h3>Meeting Confirmation</h3>"
                        f"<p>Dear {part_str if part_str != 'None specified' else 'Colleague'},</p>"
                        f"<p>You are officially scheduled for <b>{add_result.get('title', title)}</b>.</p>"
                        f"<p><b>Date & Time:</b> {add_result.get('start', date_val + ' at ' + time_val)}</p>"
                        f"<p>Please review your Google Calendar for access details.</p>"
                    )
                    
                    mail_res = GmailTool.send_email(recipient=str(recipient), subject=subj, body=body_html)
                    if mail_res.get("success"):
                        email_notice += f"\n- 📧 **Intelligent Email Notification**: Automatically sent meeting confirmation email to **`{recipient}`** via *{mail_res.get('delivery_mode')}* (Msg ID: `{mail_res.get('message_id')}`)."

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
                        f"- ⚠️ **Slot Occupied**: Requested slot (**{conf['original_time']}**) was occupied by **'{conf['conflict_with']}'**.\n"
                        f"- ✨ **New Free Slot (*Date Libre*)**: Automatically registered **'{add_result['title']}'** at **{add_result['start']}**.\n"
                        f"- **Google Calendar Integration**: {link_md}{sync_bullet}{email_notice}"
                    )
                else:
                    action_notice = (
                        f"\n\n---\n"
                        f"#### 📋 Executive Scheduling Report\n"
                        f"- ⚡ **Status**: Successfully registered **'{add_result['title']}'** on **{add_result['start']}**.\n"
                        f"- **Google Calendar Integration**: {link_md}{sync_bullet}{email_notice}"
                    )
            else:
                action_notice = f"\n\n⚠️ Could not register DB meeting: {add_result.get('error')}"

        # Step 3: Fetch updated calendar events & generate natural conversational confirmation
        calendar_data = CalendarTool.list_upcoming_meetings(filter_month=None)
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
            "You are an elite, elegant Executive Corporate Scheduling Assistant.\n"
            "Provide a crisp, natural, conversational response directly to the user in a sophisticated human voice.\n"
            "CRITICAL DESIGN RULES:\n"
            "1. DO NOT output or repeat the Prompt Engineer Mission Profile or JSON schema in your response!\n"
            "2. DO NOT duplicate links or notices if an Executive Scheduling Report is appended below.\n"
            "3. Speak naturally like a high-level human assistant without robotic templates or system formulas."
        )
        
        prompt = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": f"{context_str}User Directive: {instruction}\nMission Type: {mission}\n\nLive Database Overview:\n{events_str}{action_notice}\n\nProvide a natural, polite confirmation."}
        ]
        res = llm_client.complete(messages=prompt)
        reply = res.get("content", "Schedule inspection completed.")
        
        final_reply = mission_thinking + reply.strip()
        if action_notice and "Executive Scheduling Report" not in reply:
            final_reply += action_notice
            
        return final_reply

scheduling_agent = SchedulingAgent()
