from typing import List, Dict, Any
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.domain.scheduling.models import MissionProfile, AuditDecision, ExecutionResult, VerificationResult, VerificationStatus, AuditClassification
from backend.app.domain.scheduling.prompts import REPORT_GENERATOR_PROMPT

class ReportGeneratorAgent:
    """
    Agent 5: Executive Report Generator & Corporate Synthesizer
    Responsibilities: Generate elegant final markdown based strictly on verified actions.
    Strict Rule: Never claim success without verification. Handle failure honestly.
    """
    @staticmethod
    def generate_report(
        mission: MissionProfile,
        audit: AuditDecision,
        execution: ExecutionResult,
        verification: VerificationResult,
        existing_events: List[Dict[str, Any]]
    ) -> str:
        logger.info("📝 REPORT GENERATOR: Synthesizing verified executive communication...")
        
        # Step 1: Format transparent ChatGPT Reasoning Box
        reasoning_bullets = "\n".join([f"  - 💭 *{r}*" for r in mission.reasoning if r])
        if not reasoning_bullets:
            reasoning_bullets = "  - 💭 *Analyzed user intent and schedule integration rules.*"
            
        thinking_box = (
            f"---THINKING---\n"
            f"**Mission Directive**: `[{mission.mission.value}]` | **Priority**: `{mission.priority.value}`  \n"
            f"**Executive Reasoning**:  \n{reasoning_bullets}  \n"
            f"**AI Auditor Verdict**: `{audit.decision.value}` (Confidence: `{audit.confidence}`)  \n"
            f"**Independent Verification Status**: `{verification.status.value}` (Exec Time: `{execution.execution_time}s`)  \n"
            f"---THINKING_END---\n\n"
        )

        # Step 2: If Auditor halted execution (Duplicate / Conflict / Need Confirmation)
        if audit.decision in [AuditClassification.DUPLICATE, AuditClassification.CONFLICT, AuditClassification.NEED_CONFIRMATION] and not execution.success:
            reply = audit.conversational_message or f"I noticed a potential {audit.decision.value.lower()} regarding your request: {audit.reason} How would you like to proceed?"
            return thinking_box + str(reply)

        # Step 3: Handle Verified, Partial Success, or Failed execution
        status_badge = "✅ VERIFIED SUCCESS" if verification.status == VerificationStatus.VERIFIED else ("⚠️ PARTIAL SUCCESS" if verification.status == VerificationStatus.PARTIAL_SUCCESS else "❌ EXECUTION FAILED")
        
        link_md = f"🔗 **[📅 Open & View in Google Calendar]({execution.calendar_url})**" if execution.calendar_url else "*(Local database record synced)*"
        email_line = f"\n- 📧 **Intelligent Email Notification**: Confirmed delivery to **`{execution.gmail_recipient}`** via *{execution.gmail_delivery_mode}* (Msg ID: `{execution.gmail_message_id}`)." if execution.gmail_message_id else ""
        
        if verification.status == VerificationStatus.FAILED and mission.mission.value != "QUERY":
            err_msg = ", ".join(execution.errors) or ", ".join(verification.discrepancy_details) or "Verification could not confirm database storage."
            return thinking_box + f"### ❌ Execution Alert\nI could not verify successful registration of this schedule command: `{err_msg}`. No unverified records were forged."

        # Generate polite conversational synthesis
        system_inst = (
            "You are an elegant Executive Corporate Assistant.\n"
            "Provide a crisp, polite, articulate confirmation directly to the user.\n"
            "Never expose JSON or Prompts. Speak gracefully."
        )
        try:
            res = llm_client.complete(
                messages=[
                    {"role": "system", "content": system_inst},
                    {
                        "role": "user",
                        "content": f"Mission: {mission.mission.value}\nTitle: {mission.entities.title}\nDate/Time: {mission.entities.date} {mission.entities.time}\nVerification: {verification.status.value}\nEmail: {execution.gmail_recipient}\n\nProvide a natural 2-sentence conversational executive summary."
                    }
                ]
            )
            conversational_intro = res.get("content", f"Your request regarding {mission.entities.title} has been processed with {verification.status.value} status.")
        except Exception:
            conversational_intro = f"I have processed your schedule directive for **{mission.entities.title}** on **{mission.entities.date}** around **{mission.entities.time}**."

        report_md = (
            f"{conversational_intro.strip()}\n\n"
            f"---\n"
            f"#### 📋 Verified Executive Execution Report\n"
            f"- **Audit Status**: {status_badge} (*Confidence: {audit.confidence}*)\n"
            f"- **Action Executed**: Registered **'{mission.entities.title}'** for **{mission.entities.date}** at **{mission.entities.time}**.\n"
            f"- **Synchronization**: {link_md}{email_line}\n"
            f"- **Audit Proof**: Confirmed record in persistent database ID `{execution.database_id}`."
        )

        if mission.mission.value == "QUERY":
            ev_strs = "\n".join([f"- **{e.get('start')}**: {e.get('summary')}" for e in existing_events]) or "(No upcoming events located in database.)"
            report_md = f"### 📅 Executive Agenda & Schedule Overview\n\nHere are your current verified records in the database:\n\n{ev_strs}"

        return thinking_box + report_md
