from pathlib import Path
from django.conf import settings
import base64

from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]
BASE_DIR = Path(settings.BASE_DIR)

TOKEN_PATH = BASE_DIR / "token.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"


def get_gmail_service():
    creds = None

    if TOKEN_PATH.exists():
      creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH),
        SCOPES
    )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                   str(CREDENTIALS_PATH),
                   SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


def send_email(to, subject, body):
    service = get_gmail_service()

    message = MIMEText(body)

    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    send_message = (
        service.users()
        .messages()
        .send(
            userId="me",
            body={"raw": raw}
        )
        .execute()
    )

    return send_message

def send_bulk_email(recipients, subject, body):
    sent_emails = []
    failed_emails = []

    for recipient in recipients:
        try:
            response = send_email(
                recipient["email"],
                subject,
                body
            )

            sent_emails.append({
                 "client_id": recipient["id"],
                 "recipient": recipient["email"],
                 "thread_id": response.get("threadId"),
                 "message_id": response.get("id")
            })

        except Exception as e:
            failed_emails.append({
                "client_id": recipient["id"],
                "recipient": recipient["email"],
                "error": str(e)
            })

    return {
        "sent": sent_emails,
        "failed": failed_emails,
        "total_sent": len(sent_emails),
        "total_failed": len(failed_emails)
    }


def get_thread(thread_id):
    service = get_gmail_service()

    return service.users().threads().get(
        userId="me",
        id=thread_id
    ).execute()



def extract_plain_text(message):
    import base64
    import re

    payload = message.get("payload", {})

    def clean_text(text):
        # Decode HTML entities like &lt;
        import html
        text = html.unescape(text)

        # Remove quoted Gmail reply
        text = re.split(
            r"\s*On .*? wrote:",
            text,
            maxsplit=1,
            flags=re.DOTALL
        )[0]

        return text.strip()

    # Simple text email
    if payload.get("body", {}).get("data"):
        data = payload["body"]["data"]
        text = base64.urlsafe_b64decode(data).decode(
            "utf-8",
            errors="ignore"
        )
        return clean_text(text)

    # Multipart email
    for part in payload.get("parts", []):

        if part.get("mimeType") == "text/plain":

            data = part.get("body", {}).get("data")

            if data:
                text = base64.urlsafe_b64decode(data).decode(
                    "utf-8",
                    errors="ignore"
                )
                return clean_text(text)

    return ""
import html
import re

def check_reply(thread_id):

    thread = get_thread(thread_id)

    messages = thread.get("messages", [])

    if len(messages) <= 1:
        return {
            "replied": False,
            "reply_text": None,
            "reply_time": None,
        }

    reply = messages[-1]

    snippet = html.unescape(reply.get("snippet", ""))

    # Remove everything from "On ... wrote:" onwards
    snippet = re.sub(
        r"\n?\s*On\s.+?wrote:.*",
        "",
        snippet,
        flags=re.DOTALL,
    )

    # Remove leading "Reply"
    snippet = re.sub(
        r"^\s*Reply\s*",
        "",
        snippet,
    )

    snippet = snippet.strip()

    return {
        "replied": True,
        "reply_text": snippet,
        "reply_time": reply.get("internalDate"),
    }