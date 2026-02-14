import base64
from email.mime.text import MIMEText
from typing import Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from ..config import settings
from ..models import GmailAccount

GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
]


def build_gmail_flow(state: str | None = None) -> Flow:
    client_config = {
        'web': {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
        }
    }
    return Flow.from_client_config(
        client_config=client_config,
        scopes=GMAIL_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        state=state,
    )


def account_to_credentials(account: GmailAccount) -> Credentials:
    return Credentials(
        token=account.access_token,
        refresh_token=account.refresh_token,
        token_uri=account.token_uri or 'https://oauth2.googleapis.com/token',
        client_id=account.client_id or settings.GOOGLE_CLIENT_ID,
        client_secret=account.client_secret or settings.GOOGLE_CLIENT_SECRET,
        scopes=(account.scopes or ' '.join(GMAIL_SCOPES)).split(' '),
    )


def get_gmail_service(account: GmailAccount):
    creds = account_to_credentials(account)
    return build('gmail', 'v1', credentials=creds)


def fetch_latest_messages(account: GmailAccount, max_results: int = 10) -> list[dict[str, Any]]:
    service = get_gmail_service(account)
    result = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = result.get('messages', [])
    full_messages: list[dict[str, Any]] = []
    for msg in messages:
        msg_obj = service.users().messages().get(userId='me', id=msg['id']).execute()
        full_messages.append(msg_obj)
    return full_messages


def extract_email_fields(message: dict[str, Any]) -> dict[str, str]:
    payload = message.get('payload', {})
    headers = payload.get('headers', [])
    header_map = {h['name'].lower(): h['value'] for h in headers if 'name' in h and 'value' in h}
    return {
        'id': message.get('id', ''),
        'subject': header_map.get('subject', ''),
        'from': header_map.get('from', ''),
        'snippet': message.get('snippet', ''),
    }


def send_email(account: GmailAccount, to_email: str, subject: str, body: str) -> None:
    service = get_gmail_service(account)
    mime = MIMEText(body)
    mime['to'] = to_email
    mime['subject'] = subject
    raw_message = base64.urlsafe_b64encode(mime.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
