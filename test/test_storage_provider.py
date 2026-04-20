import json
from pathlib import Path

from carlo_bot.infrastructure.config import AppConfig
from carlo_bot.infrastructure.storage.filesystem_provider import FileSystemStorageProvider


def test_filesystem_storage_provider_loads_all_sources(tmp_path: Path):
    contacts_file = tmp_path / "contacts.json"
    contacts_file.write_text(
        json.dumps([
            {"name": "Mario", "email": "mario@example.com", "active": True},
        ]),
        encoding="utf-8",
    )

    quotes_file = tmp_path / "quotes.txt"
    quotes_file.write_text("Quote one\nQuote two\n", encoding="utf-8")

    saints_file = tmp_path / "saints.txt"
    saints_file.write_text("San Giorgio\n", encoding="utf-8")

    blasfemie_file = tmp_path / "blasfemie.txt"
    blasfemie_file.write_text("culone\n", encoding="utf-8")

    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()
    (photos_dir / "carlo.jpg").write_bytes(b"fake-image-bytes")

    config = AppConfig(
        app_env="development",
        smtp_host="smtp.gmail.com",
        smtp_port=465,
        smtp_username="user@example.com",
        smtp_password="password",
        smtp_sender="user@example.com",
        contacts_file=contacts_file.name,
        quotes_file=quotes_file.name,
        photos_dir=photos_dir.name,
        saints_file=saints_file.name,
        blasfemie_file=blasfemie_file.name,
        dry_run=True,
        storage_backend="filesystem",
        google_credentials_file="credentials.json",
        google_token_file="token.json",
        google_contacts_spreadsheet_id=None,
        google_content_spreadsheet_id=None,
        google_contacts_sheet_name="Contacts",
        google_quotes_sheet_name="Quotes",
        google_saints_sheet_name="Saints",
        google_blasfemie_sheet_name="Blasfemie",
        google_photos_folder_id=None,
    )

    provider = FileSystemStorageProvider(config=config, project_root=tmp_path)

    assert provider.load_contacts()[0]["email"] == "mario@example.com"
    assert provider.load_quotes() == ["Quote one", "Quote two"]
    assert provider.load_saints() == ["San Giorgio"]
    assert provider.load_blasfemie() == ["culone"]
    assert provider.load_photo_assets()[0].name == "carlo.jpg"