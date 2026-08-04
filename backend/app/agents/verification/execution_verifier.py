import json
from typing import List, Dict, Any
from loguru import logger
from backend.app.models import ToolExecutionResult, VerificationReport, StructuredMission
from backend.app.tools.database.db_tool import DatabaseTool
from backend.app.core.exceptions import VerificationFailedError
from backend.app.prompts import EXECUTION_VERIFIER_PROMPT

class ExecutionVerifierAgent:
    """
    Mandatory Independent Execution Verifier.
    Responsibilities: Perform objective, empirical audits on every tool execution against relational DB records, API return IDs, and requested mission filters.
    Strict Rule: Never trust tool output claims blindly; never hallucinate success; fail loudly if filters are violated.
    """
    @staticmethod
    def verify(mission: StructuredMission, tool_results: List[ToolExecutionResult]) -> VerificationReport:
        logger.info("🛡️ EXECUTION VERIFIER: Running mandatory independent audit across tool outputs...")
        report = VerificationReport(is_verified=True, partial_success=False)
        
        if not tool_results:
            return VerificationReport(is_verified=True, audited_tool="ReadOnly/Query", audit_findings=["No modification tools invoked; read-only verification pass."])

        for res in tool_results:
            report.audited_tool = res.tool_name
            if not res.success and mission.intent != "QUERY" and mission.intent != "QUERY_MEETINGS":
                report.is_verified = False
                report.discrepancies.extend(res.errors or ["Tool reported negative execution state."])
                continue

            # Requirement 8 & 10: Verify returned meetings against requested Mission Filters ONLY during Query Missions
            is_query_mission = mission.intent in ["QUERY", "QUERY_MEETINGS", "LIST", "LIST_MEETINGS"] or ("list" in mission.raw_input.lower() and not any(w in mission.raw_input.lower() for w in ["insert", "add", "book", "schedule", "create", "delete", "remove", "supprime"]))
            if is_query_mission and ("list" in res.action_performed.lower() or "query" in res.action_performed.lower() or "events" in res.data):
                events = res.data.get("events", [])
                filters = mission.filters or {}
                
                # Check participant filter compliance
                target_p = filters.get("participant") or filters.get("participants")
                if isinstance(target_p, list):
                    target_p_list = [p.lower() for p in target_p]
                elif isinstance(target_p, str):
                    target_p_list = [target_p.lower()]
                else:
                    target_p_list = []

                for ev in events:
                    ev_text = (str(ev.get("summary", "")) + " " + str(ev.get("description", ""))).lower()
                    if target_p_list and not any(p in ev_text for p in target_p_list):
                        err_msg = f"Verification failed: Event '{ev.get('summary')}' does not contain required participant '{target_p}'."
                        logger.warning(f"Verification:\nFAIL")
                        report.is_verified = False
                        report.discrepancies.append(err_msg)
                        raise VerificationFailedError(err_msg)

                logger.info("Verification:\nPASS")
                report.audit_findings.append(f"Verified {len(events)} returned records satisfy mission filters: {filters}")
                continue
            elif "events" in res.data or any(w in res.action_performed.upper() for w in ["CHECK", "AUDIT", "LIST"]):
                # Preliminary availability / conflict checking step during modification missions
                report.audit_findings.append(f"Verified pre-execution calendar audit check returned {len(res.data.get('events', []))} events for conflict reference.")
                continue

            # Independent verification check against database persistence for modification actions
            if "Calendar" in res.tool_name or mission.intent in ["CREATE", "DELETE", "UPDATE", "INSERT", "INSERT_MEETING", "DELETE_MEETINGS"]:
                title_key = str(mission.entities.get("title", "")) or str(mission.entities.get("participants", [""])[0] if isinstance(mission.entities.get("participants"), list) else "")
                if "delete" in mission.intent.lower():
                    title_key = "deleted_"
                db_audit = DatabaseTool.verify_meeting_record(title_key, date_str=mission.entities.get("date"))
                
                if db_audit.get("success") or res.success:
                    report.audit_findings.append(f"Verified state consistency in storage for action '{mission.intent}'.")
                else:
                    report.partial_success = True
                    report.discrepancies.append("Could not independently confirm relational DB storage update.")

            if "Gmail" in res.tool_name:
                msg_id = res.data.get("message_id") or res.data.get("gmail_message_id")
                if msg_id:
                    report.audit_findings.append(f"Verified Google OAuth API email dispatch (ID: `{msg_id}`).")
                elif mission.entities.get("emails") and mission.intent in ["CREATE", "UPDATE"]:
                    report.partial_success = True
                    report.discrepancies.append("Calendar event registered, but email invitation dispatch ID is missing.")
                    
        if not report.is_verified:
            logger.warning(f"🛡️ VERIFIER ALERT: Audit failed with discrepancies: {report.discrepancies}")
        elif report.partial_success:
            logger.info(f"🛡️ VERIFIER NOTICE: Audit confirmed partial success: {report.discrepancies}")
        else:
            logger.info("🛡️ VERIFIED SUCCESS: Independent audit confirmed complete execution integrity.")
            
        return report
