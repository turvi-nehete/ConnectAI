import os
import uuid
from datetime import timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# -----------------------------
# File Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TOKEN_PATH = os.path.join(BASE_DIR, "token_calendar.json")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")


# -----------------------------
# Google Calendar Scope
# -----------------------------
SCOPES = ["https://www.googleapis.com/auth/calendar"]


# -----------------------------
# Authenticate
# -----------------------------
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
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH,
            SCOPES
        )
        creds = flow.run_local_server(port=0)

    with open(TOKEN_PATH, "w") as token:
        token.write(creds.to_json())


# -----------------------------
# Google Calendar Service
# -----------------------------
service = build(
    "calendar",
    "v3",
    credentials=creds
)


# -----------------------------
# Create Meeting
# -----------------------------
def create_meeting(
    title,
    agenda,
    start_datetime,
    duration_minutes=30,
    attendees=None,
):
    """
    Creates a Google Calendar event with a Google Meet link.

    Args:
        title (str): Meeting title
        agenda (str): Meeting agenda/description
        start_datetime (datetime): Meeting start datetime
        duration_minutes (int): Meeting duration
        attendees (list[str]): List of attendee email addresses

    Returns:
        dict
    """

    if attendees is None:
        attendees = []

    end_datetime = start_datetime + timedelta(minutes=duration_minutes)

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

    conference_data = created_event.get("conferenceData", {})
    entry_points = conference_data.get("entryPoints", [])

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
            for attendee in created_event.get("attendees", [])
        ],
    }



from datetime import timedelta


def update_google_meeting(
    google_event_id,
    title,
    agenda,
    start_datetime,
    duration_minutes=30,
    attendees=None
):
    """
    Updates an existing Google Calendar event.

    Parameters:
        google_event_id (str)
        title (str)
        agenda (str)
        start_datetime (datetime)
        duration_minutes (int)
        attendees (list[str])

    Returns:
        dict
    """

    if attendees is None:
        attendees = []

    end_datetime = start_datetime + timedelta(minutes=duration_minutes)

    # Get the existing event
    event = service.events().get(
        calendarId="primary",
        eventId=google_event_id
    ).execute()

    # Update fields
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

    # Update the event
    updated_event = service.events().update(
        calendarId="primary",
        eventId=google_event_id,
        body=event,
        sendUpdates="all"      # Google emails attendees automatically
    ).execute()

    # Extract Meet link if it exists
    meet_link = ""

    conference_data = updated_event.get("conferenceData")
    if conference_data:
        entry_points = conference_data.get("entryPoints", [])
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
            for attendee in updated_event.get("attendees", [])
        ]
    }
