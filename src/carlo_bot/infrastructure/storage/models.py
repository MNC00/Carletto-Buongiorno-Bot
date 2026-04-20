from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PhotoAsset:
    # Represents a photo that can originate from either a local file path or in-memory bytes (e.g. from Google Drive)
    name: str
    path: Path | None = None
    content_bytes: bytes | None = None
    mime_type: str | None = None

    def read_bytes(self) -> bytes:
        # Returns raw photo bytes: prefers in-memory content_bytes, falls back to reading from disk
        if self.content_bytes is not None:
            return self.content_bytes

        if self.path is not None:
            return self.path.read_bytes()

        raise ValueError("Photo asset has no readable content.")