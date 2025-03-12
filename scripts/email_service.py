from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
from email.mime.text import MIMEText
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

TOKEN_FILE = "config/gmail_token.json"
CLIENT_SECRET_FILE = "config/oauth_client.json"

def get_gmail_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds

def send_email(recipient: str, subject: str, body: str):
    try:
        creds = get_gmail_credentials()
        service = build("gmail", "v1", credentials=creds)

        message = MIMEText(body)
        message["to"] = recipient
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        message = {"raw": raw_message}
        service.users().messages().send(userId="me", body=message).execute()
        
        return "Email sent successfully"
    except Exception as e:
        return f"Error: {e}"
