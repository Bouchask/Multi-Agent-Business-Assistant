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
        Uses LLM intelligence to evaluate if a requested meeting is a semantic duplicate, typo, or error
        compared to already scheduled events in the database.
        """
        override_words = ["confirm", "force", "insert anyway", "oui", "yes proceed", "ignore warning", "override", "valide", "valider"]
        if any(w in user_prompt.lower() for w in override_words):
            return {"conflict_detected": False, "reasoning": "User provided explicit authorization override."}

        if not events:
            return {"conflict_detected": False, "reasoning": "No existing calendar events found to conflict."}

        relevant_events = [e for e in events if date_str in str(e.get("start", "")) or e.get("summary", "").lower() in title.lower()]
        if not relevant_events and len(events) > 20:
            relevant_events = events[-10:]
        elif not relevant_events:
            relevant_events = events

        eval_prompt = [
            {
                "role": "system",
                "content": (
                    "You are an elite AI Semantic Deduplication & Calendar Auditor.\n"
                    "Your objective is to protect an executive's schedule from errors, typos, double-bookings, and redundant entries.\n"
                    "Analyze the New Meeting Request against the Existing Scheduled Events.\n"
                    "Examine entities closely: e.g. 'Dr. Ayoub' vs 'Ayoub', 'Dr. Yahya' vs 'Yahya', or scheduling a second meeting with the exact same person within minutes or hours on the same date.\n\n"
                    "Respond STRICTLY with a valid JSON object matching this schema:\n"
                    "{\n"
                    "  \"conflict_detected\": true/false,\n"
                    "  \"reasoning\": \"Explanation of why this appears to be a duplicate or error.\",\n"
                    "  \"existing_meeting_ref\": \"Summary of existing conflicting meeting\",\n"
                    "  \"recommended_action\": \"REQUEST_VERIFICATION\" or \"PROCEED\"\n"
                    "}\n"
                    "If a potential duplicate person or erroneous tight re-booking is detected on the same date, set conflict_detected to true and recommended_action to REQUEST_VERIFICATION.\n"
                    "If it is clearly a completely different person or distinct subject without ambiguity, set conflict_detected to false."
                )
            },
            {
                "role": "user",
                "content": f"New Meeting Request:\nTitle: {title}\nDate: {date_str}\nTime: {time_str}\n\nExisting Scheduled Events in DB:\n{json.dumps(relevant_events, indent=2)}\n\nEvaluate for semantic deduplication."
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
        
        # Step 1: Execute Prompt Engineer to convert keywords into a Structured Mission Profile with Executable Actions!
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
                "required_tool_actions": [{"tool": "CALENDAR_QUERY", "enabled": True, "reason": "Fetch meetings"}],
                "execution_goals": ["Retrieve relational DB meetings", "Generate Google Calendar detail links"],
                "success_criteria": "Schedule presented clearly to executive user."
            }
        else:
            mission_profile = prompt_engineer.generate_mission_structure(raw_prompt=instruction, domain="SCHEDULING")
            
        action = mission_profile.get("action_type", "QUERY")
        params = mission_profile.get("parameters", {})
        tool_actions = mission_profile.get("required_tool_actions", [])
        
        # Format prompt engineer structure inside clean delimiters for ChatGPT UI reasoning!
        goals_md = "\n".join([f"  - ✅ **{g}**" for g in mission_profile.get("execution_goals", ["Register schedule", "Sync with Google Calendar"])])
        tool_list_md = "\n".join([f"  - ⚡ `[{t.get('tool')}]`: *{t.get('reason')}*" for t in tool_actions if t.get("enabled", True)])
        if not tool_list_md:
            tool_list_md = "  - ⚡ `[CALENDAR_EXECUTE]`: *Standard tool workflow*"
            
        mission_thinking = (
            f"---THINKING---\n"
            f"**Mission Objective**: `{mission_profile.get('mission_title', 'Execute Schedule Directive')}`  \n"
            f"**Domain Architecture**: `{mission_profile.get('domain', 'SCHEDULING')}`  \n"
            f"**Structured Parameters**: `{json.dumps(params)}`  \n"
            f"**Intelligent Tool Execution Plan**:  \n{tool_list_md}  \n"
            f"**Execution Goals**:  \n{goals_md}  \n"
            f"**Success Criteria**: *{mission_profile.get('success_criteria', 'Verified integration')}*  \n"
            f"---THINKING_END---\n\n"
        )

        # Check if LLM explicitly demanded verification before taking action
        for ta in tool_actions:
            if ta.get("tool") == "DEMAND_CONFIRMATION" and ta.get("enabled", False) and not any(w in low_inst for w in ["confirm", "oui", "valide", "proceed"]):
                logger.info("⚡ LLM requested executive verification before executing actions.")
                verify_msg = (
                    f"### ❓ Verification & Confirmation Requested\n\n"
                    f"My AI architectural assessment indicates that we should confirm details before committing this action:\n\n"
                    f"- **Title**: `{params.get('title')}`\n"
                    f"- **Date & Time**: `{params.get('date_str')} at {params.get('time_str')}`\n"
                    f"- **Attendee / Email**: `{params.get('attendee_name') or params.get('attendee_email') or 'Not provided'}`\n\n"
                    f"**Reason**: *{ta.get('reason', 'Verify accuracy of executive scheduling parameters.')}*\n\n"
                    f"---\n"
                    f"#### ⚡ Action Required:\n"
                    f"Reply **`Confirm`** or **`Oui valider`** to execute database registration and email notification immediately!"
                )
                return mission_thinking + verify_msg

        # Step 2: Execute tool action (with Google Calendar auto-insert & conflict resolution)
        action_notice = ""
        gcal_link = ""
        email_notice = ""
        
        should_insert = action in ["CREATE", "EXECUTE"] or any(t.get("tool") == "CALENDAR_INSERT" and t.get("enabled", False) for t in tool_actions) or any(w in low_inst for w in ["insert", "add", "book", "schedule"])
        
        if should_insert:
            title = params.get("title", f"Meeting: {instruction[:30]}")
            date_val = params.get("date_str", params.get("date", "2026-08-24"))
            time_val = params.get("time_str", params.get("time", "10:00:00"))

            # --- LLM INTELLIGENT DEDUPLICATION AUDIT ---
            all_existing = CalendarTool.list_upcoming_meetings(filter_month=None).get("events", [])
            audit_res = self._evaluate_semantic_duplication(str(title), str(date_val), str(time_val), all_existing, instruction)
            
            if audit_res.get("conflict_detected") and audit_res.get("recommended_action") == "REQUEST_VERIFICATION" and not any(w in low_inst for w in ["confirm", "force", "valide"]):
                logger.warning(f"🛡️ Intercepted semantic schedule conflict for '{title}'. Halting insertion for user verification.")
                
                dedup_thinking = (
                    f"---THINKING---\n"
                    f"**Mission Objective**: `Semantic Schedule Deduplication Audit`  \n"
                    f"**Domain Architecture**: `SCHEDULING (Intelligent Guardrail)`  \n"
                    f"**Audit Findings**: `Detected possible duplicate or overlapping participant identity`  \n"
                    f"**Execution Goals**:  \n"
                    f"  - ✅ **Intercept potential duplicate calendar registration**  \n"
                    f"  - ✅ **Prevent Gmail OAuth schedule pollution & double-booking**  \n"
                    f"  - ✅ **Request executive verification from user**  \n"
                    f"**Success Criteria**: *Obtain explicit user authorization before creating overlapping event*  \n"
                    f"---THINKING_END---\n\n"
                )
                
                existing_ref = audit_res.get("existing_meeting_ref", "An existing meeting on this date")
                reasoning_exp = audit_res.get("reasoning", "The participant name matches or overlaps closely with an existing event.")
                
                interactive_warning = (
                    f"### 🛡️ Intelligent Deduplication & Schedule Audit\n\n"
                    f"I paused automatic insertion because my semantic analysis detected a potential scheduling error or duplicate entry:\n\n"
                    f"- **New Request**: `{title}` on **{date_val}** around **{time_val}**\n"
                    f"- **Existing Record Detected**: `{existing_ref}`\n\n"
                    f"**🧠 AI Intelligence & Reasoning**:\n"
                    f"> *{reasoning_exp}*\n\n"
                    f"---\n"
                    f"#### ⚡ Action Required:\n"
                    f"- If this is a separate meeting or intentional re-booking, please reply: **`Confirm insert meeting with {title}`**\n"
                    f"- If this was a typo or duplicate, no action is needed and your calendar remains clean!"
                )
                
                return dedup_thinking + interactive_warning

            # Proceed with normal DB registration & conflict slot resolution
            add_result = CalendarTool.add_meeting(title=str(title), date_str=str(date_val), time_str=str(time_val))
            
            # --- EXECUTE GMAIL NOTIFICATION IF REQUESTED BY LLM OR INSTRUCTED BY USER ---
            recipient = params.get("attendee_email")
            should_notify = any(t.get("tool") == "GMAIL_SEND" and t.get("enabled", False) for t in tool_actions) or recipient or any(w in low_inst for w in ["email", "mail", "notify", "notifie", "@"])
            
            if should_notify:
                if not recipient:
                    # Regex search for email in prompt if LLM parameter extraction missed it
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', instruction)
                    recipient = email_match.group(0) if email_match else "dr.yahya@labo.local"
                
                subj = f"Meeting Invitation & Confirmation: {add_result.get('title', title)}"
                body_html = (
                    f"<h3>Meeting Confirmation</h3>"
                    f"<p>Dear {params.get('attendee_name', 'Colleague')},</p>"
                    f"<p>You are officially scheduled for <b>{add_result.get('title', title)}</b>.</p>"
                    f"<p><b>Date & Time:</b> {add_result.get('start', date_val + ' at ' + time_val)}</p>"
                    f"<p>Please review your Google Calendar for access details.</p>"
                )
                
                mail_res = GmailTool.send_email(recipient=str(recipient), subject=subj, body=body_html)
                if mail_res.get("success"):
                    email_notice = f"\n- 📧 **Intelligent Email Notification**: Automatically sent meeting confirmation email to **`{recipient}`** via *{mail_res.get('delivery_mode')}* (Msg ID: `{mail_res.get('message_id')}`)."

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
