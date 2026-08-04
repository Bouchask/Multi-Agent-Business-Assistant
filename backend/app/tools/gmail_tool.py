import os
import os.path
from typing import Dict, Any, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from loguru import logger

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class GmailTool:
    @staticmethod
    def _get_service():
        token_path = 'credentials/token.json'
        creds = None
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as e:
                logger.warning(f"Error reading OAuth token: {e}")
        if creds and creds.valid:
            return build('gmail', 'v1', credentials=creds)
        return None

    @staticmethod
    def check_unread_emails(max_results: int = 5) -> Dict[str, Any]:
        service = GmailTool._get_service()
        if not service:
            return {
                "success": True,
                "mode": "simulation",
                "emails": [
                    {"id": "sim_101", "sender": "client@enterprise.com", "subject": "Q3 Partnership Inquiry", "snippet": "We are interested in integrating your multi-agent operating system into our operations..."},
                    {"id": "sim_102", "sender": "vp_operations@assistant.local", "subject": "Resource Allocation Budget", "snippet": "Please review the financial projection document uploaded to our business information system."}
                ]
            }
        try:
            results = service.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute()
            messages = results.get('messages', [])
            emails = []
            for msg in messages:
                m_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
                headers = m_data.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                emails.append({"id": msg['id'], "sender": sender, "subject": subject, "snippet": m_data.get('snippet', '')})
            return {"success": True, "mode": "live", "emails": emails}
        except Exception as e:
            logger.error(f"Gmail read failed: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def send_email_draft(recipient: str, subject: str, body: str) -> Dict[str, Any]:
        logger.info(f"📧 EMAIL AGENT ACTION: Drafted email to {recipient} with subject '{subject}'")
        return {"success": True, "status": "sent_draft", "recipient": recipient, "subject": subject}
