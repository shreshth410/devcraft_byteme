from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json
import logging
from datetime import datetime, timedelta

from config.config import get_config
from database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar.events"]

class GoogleCalendarService:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, db_manager: DatabaseManager):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.db_manager = db_manager
        self.service = None
        self.credentials = None

    def get_authorization_url(self, user_telegram_id: int) -> tuple[str, str]:
        config = get_config()
        flow = InstalledAppFlow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                    "javascript_origins": []
                }
            },
            SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        authorization_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true", state=str(user_telegram_id))
        return authorization_url, state

    def exchange_code_for_token(self, code: str, state: str) -> bool:
        config = get_config()
        user_telegram_id = int(state)
        flow = InstalledAppFlow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                    "javascript_origins": []
                }
            },
            SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            self.db_manager.update_user_token(user_telegram_id, json.dumps(creds.to_json()))
            self.credentials = creds
            self.service = build("calendar", "v3", credentials=self.credentials)
            return True
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return False

    def load_credentials(self, user_telegram_id: int) -> bool:
        user_data = self.db_manager.get_user(user_telegram_id)
        if user_data and user_data[0][2]:  # Check if google_calendar_token exists
            try:
                creds_json = json.loads(user_data[0][2])
                self.credentials = Credentials.from_authorized_user_info(creds_json, SCOPES)
                
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self.db_manager.update_user_token(user_telegram_id, json.dumps(self.credentials.to_json()))
                
                if self.credentials and self.credentials.valid:
                    self.service = build("calendar", "v3", credentials=self.credentials)
                    return True
            except Exception as e:
                logger.error(f"Error loading credentials from DB for user {user_telegram_id}: {e}")
        return False

    def get_upcoming_events(self, user_telegram_id: int, max_results: int = 10, days_ahead: int = 7):
        if not self.load_credentials(user_telegram_id):
            logger.warning(f"No valid credentials for user {user_telegram_id}. Cannot fetch events.")
            return []

        try:
            now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"
            events_result = self.service.events().list(
                calendarId="primary",
                timeMin=now,
                timeMax=end_time,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            events = events_result.get("items", [])
            return events
        except Exception as e:
            logger.error(f"Error fetching upcoming events for user {user_telegram_id}: {e}")
            return []

    def create_calendar_event(self, user_telegram_id: int, summary: str, description: str, start_time: str, end_time: str, timezone="America/New_York"):
        if not self.load_credentials(user_telegram_id):
            logger.warning(f"No valid credentials for user {user_telegram_id}. Cannot create event.")
            return None

        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time,
                "timeZone": timezone,
            },
        }
        try:
            event = self.service.events().insert(calendarId="primary", body=event).execute()
            logger.info("Event created: {}".format(event.get("htmlLink")))
            return event
        except Exception as e:
            logger.error(f"Error creating event for user {user_telegram_id}: {e}")
            return None

def create_google_calendar_service(client_id: str, client_secret: str, redirect_uri: str, db_manager: DatabaseManager) -> GoogleCalendarService:
    return GoogleCalendarService(client_id, client_secret, redirect_uri, db_manager)


