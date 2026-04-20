from pathlib import Path


# OAuth 2.0 scopes requested: read-only access to Drive files and Sheets data
DEFAULT_GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def get_google_credentials(
    credentials_file: Path,
    token_file: Path,
    scopes: list[str] | None = None,
):
    # Returns valid OAuth2 credentials: loads from token.json if it exists and is fresh,
    # refreshes silently if expired, or runs the browser OAuth flow to generate a new token
    scopes = scopes or DEFAULT_GOOGLE_SCOPES

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    # Attempts to reuse a previously saved token to avoid repeating the browser login
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Silently refreshes the access token using the stored refresh token
            creds.refresh(Request())
        else:
            # Opens a local browser tab for the user to grant access; saves the resulting token
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), scopes)
            creds = flow.run_local_server(port=0)

        token_file.write_text(creds.to_json(), encoding="utf-8")

    return creds


def build_drive_service(credentials_file: Path, token_file: Path):
    # Builds an authenticated Google Drive API v3 client using stored or refreshed credentials
    from googleapiclient.discovery import build

    creds = get_google_credentials(credentials_file=credentials_file, token_file=token_file)
    return build("drive", "v3", credentials=creds)


def build_sheets_service(credentials_file: Path, token_file: Path):
    # Builds an authenticated Google Sheets API v4 client using stored or refreshed credentials
    from googleapiclient.discovery import build

    creds = get_google_credentials(credentials_file=credentials_file, token_file=token_file)
    return build("sheets", "v4", credentials=creds)


if __name__ == "__main__":
    # Standalone auth helper: reads credential paths from .env and triggers the OAuth browser flow
    # Run from the project root: python -m carlo_bot.infrastructure.google.auth
    from carlo_bot.infrastructure.config import load_config
    from carlo_bot.bootstrap.runtime import get_project_root

    _config = load_config()
    _project_root = get_project_root()
    _credentials_file = _project_root / _config.google_credentials_file
    _token_file = _project_root / _config.google_token_file

    print(f"Using credentials: {_credentials_file}")
    print(f"Token will be saved to: {_token_file}")
    get_google_credentials(_credentials_file, _token_file)
    print("Authentication successful. token.json has been saved.")