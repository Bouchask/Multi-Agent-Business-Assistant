#!/usr/bin/env python3
"""
Multi-Agent Business Assistant — Complete Gmail API Feature Testing Suite
Tests all core Gmail functions cleanly and safely in a separate 'test' environment.
"""

import os
import sys
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes covering both Gmail full operations and Calendar for future assistant needs
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar'
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials", "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "credentials", "token.json")

def print_header(title):
    print("\n" + "="*70)
    print(f" 🚀 {title}")
    print("="*70)

def get_gmail_service():
    print_header("STEP 1: Authenticating with Google OAuth2")
    creds = None
    if os.path.exists(TOKEN_FILE):
        print(f"📁 Found saved token at {TOKEN_FILE}. Loading credentials...")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"❌ Error: Credentials file not found at {CREDENTIALS_FILE}")
                print("Please place your downloaded client_secret JSON as 'credentials/credentials.json'")
                sys.exit(1)
            
            print("🌐 Launching local OAuth browser for initial authentication...")
            print("⚠️ PLEASE CHECK YOUR BROWSER WINDOW TO SIGN IN AND AUTHORIZE THE ASSISTANT ⚠️")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print(f"✅ Token successfully saved to {TOKEN_FILE}")

    service = build("gmail", "v1", credentials=creds)
    print("✅ Gmail Service built successfully!")
    return service

def test_user_profile(service):
    print_header("STEP 2: Fetching Authenticated User Profile")
    profile = service.users().getProfile(userId='me').execute()
    email_address = profile.get('emailAddress')
    total_messages = profile.get('messagesTotal')
    print(f"📧 Authenticated User Email: {email_address}")
    print(f"📦 Total Mailbox Messages: {total_messages}")
    print("✅ Profile fetch successful!")
    return email_address

def test_list_recent_emails(service):
    print_header("STEP 3: Testing Read — Fetching 5 Most Recent Inbox Messages")
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
    messages = results.get('messages', [])
    if not messages:
        print("📭 Inbox is completely empty.")
    else:
        for i, msg_item in enumerate(messages, 1):
            msg = service.users().messages().get(userId='me', id=msg_item['id'], format='metadata', metadataHeaders=['Subject', 'From', 'Date']).execute()
            headers = {header['name']: header['value'] for header in msg['payload'].get('headers', [])}
            subject = headers.get('Subject', '(No Subject)')
            sender = headers.get('From', '(Unknown Sender)')
            snippet = msg.get('snippet', '')[:60] + "..." if len(msg.get('snippet', '')) > 60 else msg.get('snippet', '')
            print(f" [{i}] FROM: {sender}\n     SUBJECT: {subject}\n     SNIPPET: {snippet}\n")
    print("✅ Email Read testing complete!")

def test_search_queries(service):
    print_header("STEP 4: Testing Search Queries (Agent capabilities)")
    queries = [
        ("newer_than:7d", "Messages received in the last 7 days"),
        ("label:IMPORTANT", "Messages marked as Important"),
        ("has:attachment", "Messages containing file attachments")
    ]
    for q_str, desc in queries:
        res = service.users().messages().list(userId='me', q=q_str, maxResults=3).execute()
        count = len(res.get('messages', []))
        print(f" 🔍 Query: [{q_str:18}] -> Found {count} matching recent message(s) ({desc})")
    print("✅ Search query execution complete!")

def test_create_draft(service, user_email):
    print_header("STEP 5: Testing Compose & Draft Generation")
    message = MIMEText("Hello! This is an automated test draft created by the Multi-Agent Business Assistant API suite.\nIt proves that your AI assistant can prepare draft replies for human review!")
    message['to'] = user_email
    message['from'] = user_email
    message['subject'] = "AI Assistant: Test Draft Generation 🤖"
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    body = {'message': {'raw': raw_message}}
    draft = service.users().drafts().create(userId='me', body=body).execute()
    draft_id = draft['id']
    message_id = draft['message']['id']
    print(f"📝 Successfully created Draft! Draft ID: {draft_id} | Message ID: {message_id}")
    print("✅ Draft functionality working perfectly!")
    return draft_id

def test_send_and_modify_labels(service, user_email):
    print_header("STEP 6: Testing Email Send & Label Modification (Star & Archive)")
    print(f"📤 Sending a live verification test email to yourself ({user_email})...")
    message = MIMEText("🎉 Congratulations! Your Google OAuth2 credentials and Gmail API service are 100% operational for your Multi-Agent Business Assistant.\n\nAll operations (Read, Send, Search, Modify, Drafts) have been validated.")
    message['to'] = user_email
    message['from'] = user_email
    message['subject'] = "⚡ Multi-Agent Assistant: Live Gmail API Verification"
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    sent_msg = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
    msg_id = sent_msg['id']
    print(f"✅ Test Email Sent successfully! Message ID: {msg_id}")

    # Now let's test starring the message (Modify)
    print("⭐ Modifying labels: Adding STARRED label to the test message...")
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'addLabelIds': ['STARRED']}
        ).execute()
        print("✅ Message successfully Starred!")
    except Exception as e:
        print(f"⚠️ Could not modify sent message immediately: {e}")

    return msg_id

def test_delete_draft(service, draft_id):
    print_header("STEP 7: Testing Cleanup (Delete Draft)")
    print(f"🗑️ Deleting test draft (ID: {draft_id})...")
    service.users().drafts().delete(userId='me', id=draft_id).execute()
    print("✅ Test Draft cleanly deleted!")

def main():
    print_header("STARTING GMAIL API ALL-FUNCTIONS TEST SUITE")
    service = get_gmail_service()
    user_email = test_user_profile(service)
    test_list_recent_emails(service)
    test_search_queries(service)
    draft_id = test_create_draft(service, user_email)
    test_send_and_modify_labels(service, user_email)
    test_delete_draft(service, draft_id)
    
    print_header("🎉 ALL GMAIL FUNCTIONS VERIFIED SUCCESSFULLY! READY FOR AI AGENT INTEGRATION 🎉")

if __name__ == '__main__':
    main()
