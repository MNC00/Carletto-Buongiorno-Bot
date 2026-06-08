import os
from dataclasses import dataclass

from dotenv import find_dotenv, load_dotenv


# Immutable container holding all application configuration values parsed from .env
@dataclass
class AppConfig:
    app_env: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_sender: str
    contacts_file: str
    quotes_file: str
    photos_dir: str
    saints_file: str
    blasfemie_file: str
    dry_run: bool
    storage_backend: str
    google_credentials_file: str
    google_token_file: str
    google_contacts_spreadsheet_id: str | None
    google_content_spreadsheet_id: str | None
    google_contacts_sheet_name: str
    google_quotes_sheet_name: str
    google_saints_sheet_name: str
    google_blasfemie_sheet_name: str
    google_photos_folder_id: str | None
    unsubscribe_base_url: str | None
    unsubscribe_secret: str | None
    gemini_api_key: str | None
    llm_prompt_file: str
    birthday_prompt_file: str
    closing_rewrite_enabled: bool
    closing_rewrite_prompt_file: str


def _parse_bool(value: str) -> bool:
    # Converts common string representations (true/false/yes/no/1/0) to Python bool; raises on invalid input
    normalized = value.strip().lower()

    if normalized in {"true", "1", "yes", "y"}:
        return True

    if normalized in {"false", "0", "no", "n"}:
        return False

    raise ValueError(f"Invalid boolean value: {value}")


def load_config() -> AppConfig:
    # Loads the .env file by searching upward from this file's directory, validates required fields
    load_dotenv(find_dotenv())

    # Reads each variable with a sensible default where possible
    app_env = os.getenv("APP_ENV", "development")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_sender = os.getenv("SMTP_SENDER")
    contacts_file = os.getenv("CONTACTS_FILE", "data/contacts/contacts.json")
    quotes_file = os.getenv("QUOTES_FILE", "data/quotes/quotes.txt")
    photos_dir = os.getenv("PHOTOS_DIR", "data/photos")
    saints_file = os.getenv("SAINTS_FILE") or os.getenv("SAINTS_DIR", "data/quotes/saints.txt")
    blasfemie_file = os.getenv("BLASFEMIE_FILE") or os.getenv("BLASFEMIE_DIR", "data/quotes/blasfemie.txt")
    dry_run_raw = os.getenv("DRY_RUN", "true")
    storage_backend = os.getenv("STORAGE_BACKEND", "filesystem").strip().lower()
    google_credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "service_account.json")
    google_token_file = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    google_contacts_spreadsheet_id = _empty_to_none(os.getenv("GOOGLE_CONTACTS_SPREADSHEET_ID"))
    google_content_spreadsheet_id = _empty_to_none(os.getenv("GOOGLE_CONTENT_SPREADSHEET_ID"))
    google_contacts_sheet_name = os.getenv("GOOGLE_CONTACTS_SHEET_NAME", "Contacts")
    google_quotes_sheet_name = os.getenv("GOOGLE_QUOTES_SHEET_NAME", "Quotes")
    google_saints_sheet_name = os.getenv("GOOGLE_SAINTS_SHEET_NAME", "Saints")
    google_blasfemie_sheet_name = os.getenv("GOOGLE_BLASFEMIE_SHEET_NAME", "Blasfemie")
    google_photos_folder_id = _empty_to_none(os.getenv("GOOGLE_PHOTOS_FOLDER_ID"))
    unsubscribe_base_url = _empty_to_none(os.getenv("UNSUBSCRIBE_BASE_URL"))
    unsubscribe_secret = _empty_to_none(os.getenv("UNSUBSCRIBE_SECRET"))
    gemini_api_key = _empty_to_none(os.getenv("GEMINI_API_KEY"))
    llm_prompt_file = os.getenv("LLM_PROMPT_FILE", "apps/buongiorno-bot/data/prompts/system_prompt.txt")
    birthday_prompt_file = os.getenv("BIRTHDAY_PROMPT_FILE", "apps/buongiorno-bot/data/prompts/birthday_prompt.txt")
    closing_rewrite_enabled_raw = os.getenv("CLOSING_REWRITE_ENABLED", "true")
    closing_rewrite_prompt_file = os.getenv(
        "CLOSING_REWRITE_PROMPT_FILE",
        "apps/buongiorno-bot/data/prompts/closing_rewrite_prompt.txt",
    )

    # Validates that all required SMTP fields are present
    if not smtp_host:
        raise ValueError("Missing SMTP_HOST")
    if not smtp_port:
        raise ValueError("Missing SMTP_PORT")
    if not smtp_username:
        raise ValueError("Missing SMTP_USERNAME")
    if not smtp_password:
        raise ValueError("Missing SMTP_PASSWORD")
    if not smtp_sender:
        raise ValueError("Missing SMTP_SENDER")
    if storage_backend not in {"filesystem", "google_workspace"}:
        raise ValueError(f"Unsupported STORAGE_BACKEND: {storage_backend}")
    if (unsubscribe_base_url is None) != (unsubscribe_secret is None):
        raise ValueError("UNSUBSCRIBE_BASE_URL and UNSUBSCRIBE_SECRET must be configured together")

    # Validates Google-specific fields only when the google_workspace backend is selected
    if storage_backend == "google_workspace":
        if not google_contacts_spreadsheet_id:
            raise ValueError("Missing GOOGLE_CONTACTS_SPREADSHEET_ID")
        if not google_content_spreadsheet_id:
            raise ValueError("Missing GOOGLE_CONTENT_SPREADSHEET_ID")
        if not google_photos_folder_id:
            raise ValueError("Missing GOOGLE_PHOTOS_FOLDER_ID")

    return AppConfig(
        app_env=app_env,
        smtp_host=smtp_host,
        smtp_port=int(smtp_port),
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        smtp_sender=smtp_sender,
        contacts_file=contacts_file,
        quotes_file=quotes_file,
        photos_dir=photos_dir,
        saints_file=saints_file,
        blasfemie_file=blasfemie_file,
        dry_run=_parse_bool(dry_run_raw),
        storage_backend=storage_backend,
        google_credentials_file=google_credentials_file,
        google_token_file=google_token_file,
        google_contacts_spreadsheet_id=google_contacts_spreadsheet_id,
        google_content_spreadsheet_id=google_content_spreadsheet_id,
        google_contacts_sheet_name=google_contacts_sheet_name,
        google_quotes_sheet_name=google_quotes_sheet_name,
        google_saints_sheet_name=google_saints_sheet_name,
        google_blasfemie_sheet_name=google_blasfemie_sheet_name,
        google_photos_folder_id=google_photos_folder_id,
        unsubscribe_base_url=unsubscribe_base_url,
        unsubscribe_secret=unsubscribe_secret,
        gemini_api_key=gemini_api_key,
        llm_prompt_file=llm_prompt_file,
        birthday_prompt_file=birthday_prompt_file,
        closing_rewrite_enabled=_parse_bool(closing_rewrite_enabled_raw),
        closing_rewrite_prompt_file=closing_rewrite_prompt_file,
    )


def _empty_to_none(value: str | None) -> str | None:
    # Normalises empty or whitespace-only strings to None so callers can use simple truthiness checks
    if value is None:
        return None

    stripped = value.strip()
    return stripped or None
