from __future__ import annotations

from pathlib import Path

from app.config import AppConfig, get_config


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_gmail_service(
    credentials_path: str | Path | None = None,
    token_path: str | Path | None = None,
    config: AppConfig | None = None,
):
    """Authenticate with Gmail and return an authorized Gmail API service."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "Missing Gmail API dependencies. Install them with `pip install -r requirements.txt`."
        ) from error

    active_config = config or get_config()
    credentials_path = Path(credentials_path or active_config.credentials_path)
    token_path = Path(token_path or active_config.token_path)
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and not creds.has_scopes(SCOPES):
        creds = None

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"Gmail OAuth credentials were not found at `{credentials_path}`. "
                "Download the Desktop OAuth client JSON from Google Cloud Console "
                "and place it at that path."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
        creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)
