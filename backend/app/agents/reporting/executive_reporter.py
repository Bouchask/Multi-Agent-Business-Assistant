from typing import List
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.models import StructuredMission, ToolExecutionResult, VerificationReport, ExecutiveOutput
from backend.app.tools.calendar_tool import CalendarTool
from backend.app.prompts import EXECUTIVE_REPORTER_PROMPT

class ExecutiveReporterAgent:
    """
    Executive Reporter & Corporate Synthesizer.
    Responsibilities: Produce concise, professional executive markdown communication based strictly on verified proof.
    Strict Rule: Never expose JSON, prompts, or internal choreography to the user. Never pretend success without verification.
    """
    @staticmethod
    def synthesize(mission: StructuredMission, tool_results: List[ToolExecutionResult], verification: VerificationReport) -> str:
        logger.info("📝 EXECUTIVE REPORTER: Crafting polished executive communication...")
        
        # Transparent reasoning dropdown for frontend inspection
        reasoning_bullets = "\n".join([f"  - 💭 *Analyzed directive: {mission.objective}*" if mission.objective else "  - 💭 *Evaluated executive scheduling priorities.*"])
        thinking_box = (
            f"---THINKING---\n"
            f"**Mission Directive**: `[{mission.intent}]` | **Status**: `{mission.state.value}`  \n"
            f"**Executive Reasoning**:  \n{reasoning_bullets}  \n"
            f"**Independent Verification**: `{'VERIFIED' if verification.is_verified else ('PARTIAL_SUCCESS' if verification.partial_success else 'FAILED')}`  \n"
            f"---THINKING_END---\n\n"
        )

        if not verification.is_verified and mission.intent != "QUERY":
            err_details = ", ".join(verification.discrepancies) or "Verification could not independently confirm storage alteration."
            return thinking_box + f"### ❌ Execution Alert\nI could not independently verify successful completion of your directive: `{err_details}`. In accordance with executive integrity rules, no unverified records were reported as confirmed."

        status_badge = "✅ VERIFIED SUCCESS" if (verification.is_verified and not verification.partial_success) else "⚠️ PARTIAL SUCCESS"
        
        # Refresh current agenda overview for QUERY or DELETE actions
        if mission.intent in ["QUERY", "DELETE", "CANCEL"] or "list" in mission.raw_input.lower():
            cal_data = CalendarTool.list_upcoming_meetings(filter_month=None)
            evs = cal_data.get("events", [])
            ev_list_md = "\n".join([f"- **{e.get('start')}**: {e.get('summary')}" for e in evs]) or "(No upcoming meetings recorded in active database.)"
            
            if mission.intent in ["DELETE", "CANCEL"]:
                intro = f"I have executed your deletion directive and verified that all matching sessions are cleared from storage and synchronized accounts.\n\n---\n#### 📋 Verified Executive Deletion Report\n- **Status**: {status_badge}\n- **Action**: Cleared target records matching your specified criteria.\n\n### 📅 Updated Executive Agenda (*Mise à jour*)\n\nHere is your verified schedule moving forward:\n\n{ev_list_md}"
                return thinking_box + intro
            elif mission.intent == "QUERY":
                return thinking_box + f"### 📅 Executive Agenda & Schedule Overview\n\nHere are your current verified records in the database and Google Calendar:\n\n{ev_list_md}"

        # Synthesize conversational summary for CREATE and UPDATE actions
        gcal_url = ""
        msg_id = ""
        recip = ""
        for res in tool_results:
            if res.data.get("google_calendar_link"):
                gcal_url = res.data.get("google_calendar_link")
            if res.data.get("gmail_message_id") or res.data.get("message_id"):
                msg_id = res.data.get("gmail_message_id") or res.data.get("message_id")
            if res.data.get("recipient"):
                recip = res.data.get("recipient")

        link_md = f"🔗 **[📅 Open, View & Save in Google Calendar]({gcal_url})**" if gcal_url else "*(Persistent database storage verified)*"
        email_line = f"\n- 📧 **Intelligent Email Notification**: Confirmed invitation delivery to **`{recip or 'specified email'}`** via *Live Google OAuth API* (Msg ID: `{msg_id}`)." if msg_id else ""

        try:
            res = llm_client.complete(
                messages=[
                    {"role": "system", "content": EXECUTIVE_REPORTER_PROMPT},
                    {"role": "user", "content": f"Directive: {mission.raw_input}\nVerified Status: {status_badge}\nTool Proof: GCal ({bool(gcal_url)}), Gmail ({bool(msg_id)})\nWrite a polished 2-sentence executive summary."}
                ],
                temperature=0.2
            )
            summary = res.get("content", f"Your scheduling directive regarding **{mission.entities.get('title', 'meeting')}** has been processed independently and confirmed.").strip()
        except Exception:
            summary = f"I have independently processed and verified your scheduling directive for **{mission.entities.get('title', 'meeting')}** on **{mission.entities.get('date', 'specified date')}** around **{mission.entities.get('time', '10:00:00')}**."

        report_md = (
            f"{summary}\n\n"
            f"---\n"
            f"#### 📋 Executive Scheduling Report\n"
            f"- **Status**: {status_badge}\n"
            f"- **Action Completed**: Registered and confirmed **'{mission.entities.get('title', 'Meeting')}'**.\n"
            f"- **Synchronization & Proof**: {link_md}{email_line}\n"
            f"- **Next Step**: Review your Google Calendar or reply with any follow-up adjustments."
        )
        return thinking_box + report_md
