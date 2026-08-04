from loguru import logger
from backend.app.tools.gmail_tool import GmailTool
from backend.app.llm.client import llm_client

class EmailAgent:
    def run(self, instruction: str) -> str:
        logger.info(f"📧 EMAIL AGENT executing instructions: '{instruction}'")
        if "draft" in instruction.lower() or "send" in instruction.lower():
            res = GmailTool.send_email_draft(recipient="executive@client.org", subject="Follow-up on Business Collaboration", body=instruction)
            return f"[Email Agent] Successfully created professional correspondence draft to {res['recipient']} regarding '{res['subject']}'."
        else:
            emails = GmailTool.check_unread_emails()
            emails_str = "\n".join([f"- From {e['sender']} | Subject: '{e['subject']}' | Snippet: {e['snippet']}" for e in emails.get("emails", [])])
            prompt = [
                {"role": "system", "content": "You are the Executive Email Communications Agent. Summarize unread priority correspondence clearly."},
                {"role": "user", "content": f"Unread emails:\n{emails_str}\n\nSummarize key actionable items for the leadership team."}
            ]
            res = llm_client.complete(messages=prompt)
            return res.get("content", "Email triage completed.")

email_agent = EmailAgent()
