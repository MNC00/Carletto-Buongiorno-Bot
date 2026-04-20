from pathlib import Path

from carlo_bot.infrastructure.config import AppConfig
from carlo_bot.infrastructure.google.auth import build_drive_service, build_sheets_service
from carlo_bot.infrastructure.google.contacts_sheet import GoogleContactsSheet
from carlo_bot.infrastructure.google.content_sheet import GoogleContentSheet
from carlo_bot.infrastructure.google.drive_storage import GoogleDrivePhotoStorage
from carlo_bot.infrastructure.storage.models import PhotoAsset
from carlo_bot.infrastructure.storage.provider import StorageProvider


class GoogleWorkspaceStorageProvider(StorageProvider):
    # StorageProvider implementation that reads all data from Google Sheets and Google Drive
    def __init__(self, config: AppConfig, project_root: Path) -> None:
        credentials_file = project_root / config.google_credentials_file
        token_file = project_root / config.google_token_file

        # Contacts live in a dedicated spreadsheet; content (quotes/saints/blasfemie) live in a separate one
        self._contacts_reader = GoogleContactsSheet(
            sheets_service=build_sheets_service(credentials_file, token_file),
            spreadsheet_id=_required(config.google_contacts_spreadsheet_id, "GOOGLE_CONTACTS_SPREADSHEET_ID"),
            sheet_name=config.google_contacts_sheet_name,
        )
        self._content_reader = GoogleContentSheet(
            sheets_service=build_sheets_service(credentials_file, token_file),
            spreadsheet_id=_required(config.google_content_spreadsheet_id, "GOOGLE_CONTENT_SPREADSHEET_ID"),
        )
        self._photo_storage = GoogleDrivePhotoStorage(
            drive_service=build_drive_service(credentials_file, token_file),
            folder_id=_required(config.google_photos_folder_id, "GOOGLE_PHOTOS_FOLDER_ID"),
        )
        # Sheet names are configurable per env so the same code works for different locales
        self._quotes_sheet_name = config.google_quotes_sheet_name
        self._saints_sheet_name = config.google_saints_sheet_name
        self._blasfemie_sheet_name = config.google_blasfemie_sheet_name

    def load_contacts(self) -> list[dict]:
        # Delegates to the contacts sheet reader which maps rows to name/email/active dicts
        return self._contacts_reader.load_contacts()

    def load_quotes(self) -> list[str]:
        # Reads the quotes tab from the content spreadsheet and returns active values
        return self._content_reader.load_values(self._quotes_sheet_name)

    def load_saints(self) -> list[str]:
        # Reads the saints tab from the content spreadsheet and returns active values
        return self._content_reader.load_values(self._saints_sheet_name)

    def load_blasfemie(self) -> list[str]:
        # Reads the blasfemie tab from the content spreadsheet and returns active values
        return self._content_reader.load_values(self._blasfemie_sheet_name)

    def load_photo_assets(self) -> list[PhotoAsset]:
        # Lists and downloads all images from the configured Google Drive folder
        return self._photo_storage.load_photo_assets()


def _required(value: str | None, field_name: str) -> str:
    # Asserts a config value is present; raises with a clear message so the user knows which variable to set
    if value is None:
        raise ValueError(f"Missing {field_name}")
    return value