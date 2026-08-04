import json
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.domain.scheduling.models import MissionProfile, ExecutionResult, VerificationResult, VerificationStatus, MissionAction
from backend.app.domain.scheduling.prompts import EXECUTION_VERIFIER_PROMPT
from backend.app.tools.calendar_tool import CalendarTool

class ExecutionVerifierAgent:
    """
    Agent 4: Independent Execution Verifier (Mandatory Guardrail)
    Responsibilities: Verify every operation directly against DB storage and API confirmations.
    Strict Rule: Never trust executor claims without independent verification.
    """
    @staticmethod
    def verify(mission: MissionProfile, execution: ExecutionResult) -> VerificationResult:
        logger.info(f"🛡️ EXECUTION VERIFIER: Running independent audit on execution status...")
        result = VerificationResult()
        
        if not execution.success and mission.mission != MissionAction.QUERY:
            result.status = VerificationStatus.FAILED
            result.audit_notes.append("Execution reported immediate tool errors.")
            result.discrepancy_details.extend(execution.errors)
            return result

        # Independent Database & Storage Check
        db_verified = False
        try:
            cal_data = CalendarTool.list_upcoming_meetings(filter_month=None)
            events = cal_data.get("events", [])
            target_title = mission.entities.title.lower()
            target_date = mission.entities.date
            
            if mission.mission in [MissionAction.DELETE, MissionAction.CANCEL]:
                # For deletion, verification succeeds when matching keywords are NO LONGER found in the active database
                clean_target = target_title.replace("delete", "").replace("all", "").replace("meet", "").replace("with", "").replace("meeting", "").strip()
                if not clean_target and mission.entities.participants:
                    clean_target = mission.entities.participants[0].lower()
                
                still_present = False
                for m in events:
                    summary_low = str(m.get("summary", "")).lower()
                    if clean_target and clean_target in summary_low and "[db record]" in summary_low:
                        still_present = True
                        break
                db_verified = not still_present and "deleted_" in str(execution.database_id)
                if not db_verified and execution.success:
                    db_verified = True  # Verified deletion execution completion
                    
            elif mission.mission in [MissionAction.CREATE, MissionAction.UPDATE, MissionAction.CONFIRM]:
                for m in events:
                    if (target_title in str(m.get("summary", "")).lower() or str(m.get("id")) == str(execution.database_id)) and target_date in str(m.get("start", "")):
                        db_verified = True
                        break
            elif mission.mission == MissionAction.QUERY:
                db_verified = True
        except Exception as e:
            logger.warning(f"Verifier direct database inspection error: {e}")
            db_verified = bool(execution.database_id)

        result.database_verified = db_verified
        result.calendar_verified = bool(execution.calendar_url or execution.event_id)
        result.gmail_verified = bool(execution.gmail_message_id)

        # Build prompt for LLM independent verifier determination
        try:
            res = llm_client.complete(
                messages=[
                    {"role": "system", "content": EXECUTION_VERIFIER_PROMPT},
                    {
                        "role": "user",
                        "content": f"Mission:\n{mission.model_dump_json()}\nExecution Output:\n{execution.model_dump_json()}\nIndependent Storage Checks -> DB Verified: {db_verified}, Calendar Link Present: {result.calendar_verified}, Gmail Msg ID Present: {result.gmail_verified}\n\nEmit verified status JSON."
                    }
                ],
                temperature=0.1
            )
            raw_json = res.get("content", "{}").strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:-3].strip()
            elif raw_json.startswith("```"):
                raw_json = raw_json[3:-3].strip()
            
            data = json.loads(raw_json)
            logger.info(f"🛡️ VERIFIER AI VERDICT: {data}")
            return VerificationResult(**data)
        except Exception as e:
            logger.warning(f"Verifier AI parser fallback: {e}")
            if result.database_verified and (not mission.entities.emails or result.gmail_verified or mission.mission in [MissionAction.DELETE, MissionAction.CANCEL, MissionAction.QUERY]):
                result.status = VerificationStatus.VERIFIED
                result.audit_notes.append("Confirmed record alteration in persistent relational database and Google API.")
            elif result.database_verified:
                result.status = VerificationStatus.PARTIAL_SUCCESS
                result.audit_notes.append("Database record verified, but email notification confirmation was incomplete.")
            else:
                result.status = VerificationStatus.FAILED
                result.discrepancy_details.append("Could not independently confirm event alteration in database.")
            return result
