import re
from loguru import logger
from backend.app.models import DomainExecutionRequest, DomainType, TaskDefinition

class EmailDomainAgent:
    """
    Email Domain Reasoning Agent.
    Responsibilities: Formulate email invitation strategy and validate target addresses.
    Strict Rule: NEVER calls Gmail APIs directly; outputs structured DomainExecutionRequest.
    """
    @staticmethod
    def reason(task: TaskDefinition, context: str = "") -> DomainExecutionRequest:
        logger.info(f"📧 EMAIL DOMAIN AGENT: Formulating email notification strategy for task '{task.task_name}'")
        params = task.parameters or {}
        emails = params.get("emails", [])
        if not emails and params.get("participants"):
            for p in params.get("participants", []):
                if "@" in str(p):
                    emails.append(str(p))
                    
        title = params.get("title", "Executive Appointment")
        date_str = params.get("date", "Scheduled date")
        time_str = params.get("time", "10:00 AM")
        
        subj = f"Meeting Invitation & Confirmation: {title}"
        html_body = (
            f"<h3>Meeting Confirmation</h3>"
            f"<p>Dear Colleague,</p>"
            f"<p>You are officially confirmed for <b>{title}</b>.</p>"
            f"<p><b>Date & Time:</b> {date_str} at {time_str}</p>"
            f"<p>Please review your Google Calendar for sync credentials.</p>"
        )
        
        return DomainExecutionRequest(
            domain=DomainType.EMAIL,
            action_type="SEND_EMAIL",
            target_tool="GmailTool",
            parameters={"recipient": emails[0] if emails else "colleague@assistant.local", "subject": subj, "body": html_body, "recipients_list": emails},
            requires_user_confirmation=False
        )
