from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import uvicorn
import logging

from config.config import get_config
from api_integrations.google_calendar import GoogleCalendarService
from database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize DatabaseManager and GoogleCalendarService
db_manager = DatabaseManager()
config = get_config()
google_calendar_service = GoogleCalendarService(
    client_id=config["GOOGLE_CLIENT_ID"],
    client_secret=config["GOOGLE_CLIENT_SECRET"],
    redirect_uri=config["WEBHOOK_URL"] + "/oauth2callback",
    db_manager=db_manager
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/auth/google/start/{user_id}")
async def google_auth_start(user_id: int):
    try:
        authorization_url, state = google_calendar_service.get_authorization_url(user_id)
        return RedirectResponse(authorization_url)
    except Exception as e:
        logger.error(f"Error starting Google auth flow for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")  # This is our user_id

    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")

    user_id = int(state)

    if google_calendar_service.exchange_code_for_token(code, user_id):
        return {"message": f"Google Calendar connected successfully for user {user_id}! You can now close this window."}
    else:
        raise HTTPException(status_code=500, detail="Failed to exchange code for token.")

@app.get("/api/calendar/status/{user_id}")
async def get_calendar_status(user_id: int):
    authenticated = google_calendar_service.load_credentials(user_id)
    return {"authenticated": authenticated}

@app.get("/api/calendar/events/{user_id}")
async def get_calendar_events(user_id: int, max_results: int = 10, days_ahead: int = 7):
    events = google_calendar_service.get_upcoming_events(user_id, max_results, days_ahead)
    return {"events": events}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=config["WEBHOOK_PORT"])

