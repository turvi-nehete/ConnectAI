import os
import uuid
from datetime import timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# -----------------------------------
# Secret File Paths
# -----------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Local development
LOCAL_CREDENTIALS = os.path.join(BASE_DIR, "credentials.json")
LOCAL_TOKEN = os.path.join(BASE_DIR, "token_calendar.json")

# Render Secret Files
RENDER_CREDENTIALS = "/etc/secrets/credentials.json"
RENDER_TOKEN = "/etc/secrets/token_calendar.json"

# Automatically use Render files if they exist
CREDENTIALS_PATH = (
    RENDER_CREDENTIALS
    if os.path.exists(RENDER_CREDENTIALS)
    else LOCAL_CREDENTIALS
)

TOKEN_PATH = (
    RENDER_TOKEN
    if os.path.exists(RENDER_TOKEN)
    else LOCAL_TOKEN
)


# -----------------------------------
# Google Calendar Scope
# -----------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


# -----------------------------------
# Calendar Service
# -----------------------------------

def get_calendar_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(
            TOKEN_PATH,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:

            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Google credentials not found: {CREDENTIALS_PATH}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

            # Save token only for local development
            if TOKEN_PATH == LOCAL_TOKEN:
                with open(TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())

    return build(
        "calendar",
        "v3",
        credentials=creds
    )


# -----------------------------------
# Create Meeting
# -----------------------------------

def create_meeting(
    title,
    agenda,
    start_datetime,
    duration_minutes=30,
    attendees=None,
):

    service = get_calendar_service()

    if attendees is None:
        attendees = []

    end_datetime = start_datetime + timedelta(
        minutes=duration_minutes
    )

    event = {
        "summary": title,
        "description": agenda,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "attendees": [
            {"email": email}
            for email in attendees
        ],
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {
                    "type": "hangoutsMeet"
                }
            }
        }
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1,
        sendUpdates="all",
    ).execute()

    meet_link = None

    conference_data = created_event.get(
        "conferenceData",
        {}
    )

    entry_points = conference_data.get(
        "entryPoints",
        []
    )

    for entry in entry_points:
        if entry.get("entryPointType") == "video":
            meet_link = entry.get("uri")
            break

    return {
        "event_id": created_event["id"],
        "meet_link": meet_link,
        "calendar_link": created_event["htmlLink"],
        "start": created_event["start"]["dateTime"],
        "end": created_event["end"]["dateTime"],
        "attendees": [
            attendee["email"]
            for attendee in created_event.get(
                "attendees",
                []
            )
        ],
    }


# -----------------------------------
# Update Meeting
# -----------------------------------

def update_google_meeting(
    google_event_id,
    title,
    agenda,
    start_datetime,
    duration_minutes=30,
    attendees=None,
):

    service = get_calendar_service()

    if attendees is None:
        attendees = []

    end_datetime = start_datetime + timedelta(
        minutes=duration_minutes
    )

    event = service.events().get(
        calendarId="primary",
        eventId=google_event_id
    ).execute()

    event["summary"] = title
    event["description"] = agenda

    event["start"] = {
        "dateTime": start_datetime.isoformat(),
        "timeZone": "Asia/Kolkata",
    }

    event["end"] = {
        "dateTime": end_datetime.isoformat(),
        "timeZone": "Asia/Kolkata",
    }

    event["attendees"] = [
        {"email": email}
        for email in attendees
    ]

    updated_event = service.events().update(
        calendarId="primary",
        eventId=google_event_id,
        body=event,
        sendUpdates="all"
    ).execute()

    meet_link = ""

    conference_data = updated_event.get("conferenceData")

    if conference_data:
        entry_points = conference_data.get(
            "entryPoints",
            []
        )

        if entry_points:
            meet_link = entry_points[0]["uri"]

    return {
        "event_id": updated_event["id"],
        "meet_link": meet_link,
        "calendar_link": updated_event["htmlLink"],
        "start": updated_event["start"]["dateTime"],
        "end": updated_event["end"]["dateTime"],
        "attendees": [
            attendee["email"]
            for attendee in updated_event.get(
                "attendees",
                []
            )
        ]
    }