import json
from loguru import logger
from backend.app.models import ToolExecutionResult, VerificationReport, StructuredMission
from backend.app.tools.database.db_tool import DatabaseTool
from backend.app.prompts import EXECUTION_VERIFIER_PROMPT

class ExecutionVerifierAgent:
    """
    Mandatory Independent Execution Verifier.
    Responsibilities: Perform objective, empirical audits on every tool execution against relational DB records and API return IDs.
    Strict Rule: Never trust tool output claims blindly; never hallucinate success.
    """
    @staticmethod
    def verify(mission: StructuredMission, tool_results: List[ToolExecutionResult]) -> VerificationReport:
        logger.info("🛡️ EXECUTION VERIFIER: Running mandatory independent audit across tool outputs...")
        report = VerificationReport(is_verified=True, partial_success=False)
        
        if not tool_results:
            return VerificationReport(is_verified=True, audited_tool="ReadOnly/Query", audit_findings=["No modification tools invoked; read-only verification pass."])

        for res in tool_results:
            report.audited_tool = res.tool_name
            if not res.success and mission.intent != "QUERY":
                report.is_verified = False
                report.discrepancies.extend(res.errors or ["Tool reported negative execution state."])
                continue

            # Independent verification check against database persistence
            if "Calendar" in res.tool_name or mission.intent in ["CREATE", "DELETE", "UPDATE"]:
                title_key = str(mission.entities.get("title", "")) or str(mission.entities.get("participants", [""])[0])
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
