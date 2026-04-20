import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


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


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()

    if normalized in {"true", "1", "yes", "y"}:
        return True

    if normalized in {"false", "0", "no", "n"}:
        return False

    raise ValueError(f"Invalid boolean value: {value}")


def load_config() -> AppConfig:
    project_root = Path(__file__).resolve().parents[3]
    env_path = project_root / ".env"

    load_dotenv(dotenv_path=env_path)

    app_env = os.getenv("APP_ENV", "development")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_sender = os.getenv("SMTP_SENDER")
    contacts_file = os.getenv("CONTACTS_FILE", "data/contacts/contacts.json")
    quotes_file = os.getenv("QUOTES_FILE", "data/quotes/quotes.txt")
    photos_dir = os.getenv("PHOTOS_DIR", "data/photos")
    saints_file = os.getenv("SAINTS_FILE", "data/quotes/saints.txt")
    blasfemie_file = os.getenv("BLASFEMIE_FILE", "data/quotes/blasfemie.txt")
    dry_run_raw = os.getenv("DRY_RUN", "true")

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
    )
