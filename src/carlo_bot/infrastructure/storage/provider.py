from abc import ABC, abstractmethod
from pathlib import Path

from carlo_bot.infrastructure.config import AppConfig
from carlo_bot.infrastructure.storage.models import PhotoAsset


class StorageProvider(ABC):
    # Abstract base class defining the contract all storage backends must implement
    @abstractmethod
    def load_contacts(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def load_quotes(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def load_saints(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def load_blasfemie(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def load_photo_assets(self) -> list[PhotoAsset]:
        raise NotImplementedError


def build_storage_provider(config: AppConfig, project_root: Path) -> StorageProvider:
    # Factory: instantiates the correct backend (filesystem or Google Workspace) based on STORAGE_BACKEND
    if config.storage_backend == "filesystem":
        from carlo_bot.infrastructure.storage.filesystem_provider import FileSystemStorageProvider

        return FileSystemStorageProvider(config=config, project_root=project_root)

    if config.storage_backend == "google_workspace":
        from carlo_bot.infrastructure.google.provider import GoogleWorkspaceStorageProvider

        return GoogleWorkspaceStorageProvider(config=config, project_root=project_root)

    raise ValueError(f"Unsupported storage backend: {config.storage_backend}")