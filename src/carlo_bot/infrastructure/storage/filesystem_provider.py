from pathlib import Path

from carlo_bot.domain.loaders import load_blasfemie, load_contacts, load_photo_paths, load_quotes, load_saints
from carlo_bot.infrastructure.config import AppConfig
from carlo_bot.infrastructure.storage.models import PhotoAsset
from carlo_bot.infrastructure.storage.provider import StorageProvider


class FileSystemStorageProvider(StorageProvider):
    # Reads all datasets from local files; paths are resolved at construction time from config + project root
    def __init__(self, config: AppConfig, project_root: Path) -> None:
        self._contacts_path = project_root / config.contacts_file
        self._quotes_path = project_root / config.quotes_file
        self._saints_path = project_root / config.saints_file
        self._blasfemie_path = project_root / config.blasfemie_file
        self._photos_path = project_root / config.photos_dir

    def load_contacts(self) -> list[dict]:
        # Delegates to domain loader which parses and validates the JSON contacts file
        return load_contacts(self._contacts_path)

    def load_quotes(self) -> list[str]:
        # Delegates to domain loader which reads the quotes text file line by line
        return load_quotes(self._quotes_path)

    def load_saints(self) -> list[str]:
        # Delegates to domain loader which reads the saints text file line by line
        return load_saints(self._saints_path)

    def load_blasfemie(self) -> list[str]:
        # Delegates to domain loader which reads the blasfemie text file line by line
        return load_blasfemie(self._blasfemie_path)

    def load_photo_assets(self) -> list[PhotoAsset]:
        # Wraps each discovered local image path in a PhotoAsset with path-based lazy loading
        return [PhotoAsset(name=path.name, path=path) for path in load_photo_paths(self._photos_path)]