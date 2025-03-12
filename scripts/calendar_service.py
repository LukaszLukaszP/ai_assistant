from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]

TOKEN_FILE = "config/token.json"
CLIENT_SECRET_FILE = "config/oauth_client.json"  # Plik pobrany z Google Cloud

def get_credentials():
    creds = None
    # Sprawdź, czy mamy już zapisany token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # Jeśli nie ma zapisanego tokenu, przeprowadź autoryzację
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        creds = flow.run_local_server(port=0)  # Otworzy lokalny serwer na potrzeby autoryzacji
        # Zapisz token do pliku, żeby nie trzeba było autoryzować za każdym razem
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds

credentials = get_credentials()
calendar_service = build("calendar", "v3", credentials=credentials)

def add_calendar_event(summary: str, start_time: str, end_time: str):
    event = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": "Europe/Warsaw"},
        "end": {"dateTime": end_time, "timeZone": "Europe/Warsaw"},
    }
    event_result = calendar_service.events().insert(calendarId="primary", body=event).execute()
    return f"Event added: {event_result['id']}"
