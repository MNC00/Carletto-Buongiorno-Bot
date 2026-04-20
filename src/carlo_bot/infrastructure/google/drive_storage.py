import mimetypes

from carlo_bot.infrastructure.storage.models import PhotoAsset


class GoogleDrivePhotoStorage:
    # Lists and downloads image files from a specific Google Drive folder using the Drive API v3
    def __init__(self, drive_service, folder_id: str) -> None:
        self._service = drive_service
        self._folder_id = folder_id

    def load_photo_assets(self) -> list[PhotoAsset]:
        # Queries Drive for all non-trashed image files in the folder, downloads each one eagerly
        response = (
            self._service.files()
            .list(
                q=(
                    f"'{self._folder_id}' in parents and trashed = false and "
                    "mimeType contains 'image/'"
                ),
                fields="files(id, name, mimeType)",
                pageSize=1000,
            )
            .execute()
        )
        files = response.get("files", [])
        assets = []
        for file_item in files:
            name = file_item["name"]
            # Uses the MIME type reported by Drive; falls back to guessing from the filename
            mime_type = file_item.get("mimeType") or mimetypes.guess_type(name)[0]
            assets.append(
                PhotoAsset(
                    name=name,
                    content_bytes=self._download_file(file_item["id"]),
                    mime_type=mime_type,
                )
            )

        if not assets:
            raise ValueError("Google Drive photos folder has no valid images.")

        return assets

    def _download_file(self, file_id: str) -> bytes:
        # Downloads a Drive file by ID into an in-memory buffer and returns the raw bytes
        from googleapiclient.http import MediaIoBaseDownload
        import io

        request = self._service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        return buffer.getvalue()