import time
from loguru import logger
from backend.app.domain.scheduling.models import MissionProfile, ExecutionResult, MissionAction
from backend.app.tools.calendar_tool import CalendarTool
from backend.app.tools.gmail_tool import GmailTool

class CalendarExecutorAgent:
    """
    Agent 3: Calendar & Gmail Executor
    Responsibilities: Execute tools strictly, return structured ExecutionResult data.
    Strict Rule: Never generate user text, never explain, never reason. Pure tool orchestrator.
    """
    @staticmethod
    def execute(mission: MissionProfile) -> ExecutionResult:
        start_t = time.time()
        result = ExecutionResult(action_attempted=mission.mission.value)
        logger.info(f"⚙️ CALENDAR EXECUTOR: Running tool execution for mission '{mission.mission.value}'")
        
        try:
            if mission.mission in [MissionAction.CREATE, MissionAction.UPDATE, MissionAction.CONFIRM]:
                title = mission.entities.title
                date_str = mission.entities.date
                time_str = mission.entities.time
                
                # Execute Google Calendar / DB insertion
                add_res = CalendarTool.add_meeting(title=str(title), date_str=str(date_str), time_str=str(time_str))
                
                if add_res.get("success"):
                    result.success = True
                    result.database_id = str(add_res.get("id", f"db_{hash(title + date_str) % 10000}"))
                    result.event_id = add_res.get("gcal_event_id", "gcal_oauth_synced")
                    result.calendar_url = add_res.get("google_calendar_link", "")
                    
                    if add_res.get("conflict_resolved"):
                        conf = add_res["conflict_details"]
                        result.warnings.append(f"Slot conflict at {conf['original_time']} resolved via Date Libre shifting to {add_res['start']}.")
                else:
                    result.success = False
                    result.errors.append(str(add_res.get("error", "Failed to commit database meeting record.")))
                
                # Execute Gmail Notification if attendees/emails exist
                recipients = mission.entities.emails
                if not recipients and mission.entities.participants:
                    for p in mission.entities.participants:
                        if "@" in p:
                            recipients.append(p)
                            
                if recipients and result.success:
                    for recipient in recipients:
                        subj = f"Meeting Invitation & Confirmation: {title}"
                        body_html = (
                            f"<h3>Meeting Confirmation</h3>"
                            f"<p>Dear Colleague,</p>"
                            f"<p>You are officially scheduled for <b>{title}</b>.</p>"
                            f"<p><b>Date & Time:</b> {add_res.get('start', f'{date_str} {time_str}')}</p>"
                            f"<p><b>Location:</b> {mission.entities.location}</p>"
                            f"<p>Please review your Google Calendar for access credentials.</p>"
                        )
                        mail_res = GmailTool.send_email(recipient=str(recipient), subject=subj, body=body_html)
                        if mail_res.get("success"):
                            result.gmail_message_id = mail_res.get("message_id", "msg_verified_oauth")
                            result.gmail_recipient = recipient
                            result.gmail_delivery_mode = mail_res.get("delivery_mode", "Live OAuth API")
                        else:
                            result.warnings.append(f"Gmail notification dispatch error for {recipient}: {mail_res.get('error')}")

            elif mission.mission == MissionAction.QUERY:
                result.success = True
                result.database_id = "query_overview_only"

        except Exception as e:
            logger.error(f"Executor runtime exception: {e}")
            result.success = False
            result.errors.append(str(e))
            
        result.execution_time = round(time.time() - start_t, 3)
        logger.info(f"⚙️ EXECUTOR RESULT: {result.model_dump_json()}")
        return result
