import mimetypes
from email.message import EmailMessage
from pathlib import Path

from carlo_bot.infrastructure.storage.models import PhotoAsset


# Content-ID used to reference the inline photo in the HTML body via cid:carlo_photo
INLINE_IMAGE_CID = "carlo_photo"


def _build_inline_message(
    sender: str,
    recipients: list[str],
    subject: str,
    plain_body: str,
    html_body: str,
    image_name: str,
    image_data: bytes,
    mime_type: str | None,
) -> EmailMessage:
    # Builds a multipart/alternative MIME message and attaches the image inline using the CID reference
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)

    message.set_content(plain_body)
    message.add_alternative(html_body, subtype="html")

    # Guesses MIME type from filename if not provided; falls back to octet-stream
    if mime_type is None:
        mime_type, _ = mimetypes.guess_type(image_name)

    if mime_type is None:
        mime_type = "application/octet-stream"

    maintype, subtype = mime_type.split("/", 1)

    # Attaches the image bytes as a related inline part on the HTML alternative
    html_part = message.get_payload()[-1]
    html_part.add_related(
        image_data,
        maintype=maintype,
        subtype=subtype,
        cid=f"<{INLINE_IMAGE_CID}>",
        filename=image_name,
        disposition="inline",
    )

    return message


def _build_attachment_message(
    sender: str,
    recipients: list[str],
    subject: str,
    body: str,
    attachment_path: Path,
) -> EmailMessage:
    # Builds a simple message with a file attached as a downloadable attachment
    if not attachment_path.exists():
        raise FileNotFoundError(f"Attachment file not found: {attachment_path}")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    mime_type, _ = mimetypes.guess_type(attachment_path.name)
    if mime_type is None:
        mime_type = "application/octet-stream"

    maintype, subtype = mime_type.split("/", 1)
    with open(attachment_path, "rb") as file:
        attachment_data = file.read()

    message.add_attachment(
        attachment_data,
        maintype=maintype,
        subtype=subtype,
        filename=attachment_path.name,
    )
    return message


def build_email_message(
    sender: str,
    recipients: list[str],
    subject: str,
    plain_body: str | None = None,
    html_body: str | None = None,
    image_path: Path | None = None,
    image_asset: PhotoAsset | None = None,
    *,
    body: str | None = None,
    attachment_path: Path | None = None,
) -> EmailMessage:
    # Public factory: routes to inline or attachment message builder depending on the provided arguments
    if not recipients:
        raise ValueError("Recipients list cannot be empty.")

    if plain_body is not None or html_body is not None or image_path is not None or image_asset is not None:
        if plain_body is None or html_body is None:
            raise ValueError("plain_body and html_body must be provided for inline email mode.")
        if image_path is not None and image_asset is not None:
            raise ValueError("Use either image_path or image_asset, not both.")

        # Uses a PhotoAsset (supports both filesystem and in-memory bytes from Google Drive)
        if image_asset is not None:
            return _build_inline_message(
                sender,
                recipients,
                subject,
                plain_body,
                html_body,
                image_asset.name,
                image_asset.read_bytes(),
                image_asset.mime_type,
            )
        if image_path is None:
            raise ValueError("plain_body, html_body, and image_path must be provided together.")
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        return _build_inline_message(
            sender,
            recipients,
            subject,
            plain_body,
            html_body,
            image_path.name,
            image_path.read_bytes(),
            mimetypes.guess_type(image_path.name)[0],
        )

    if body is not None or attachment_path is not None:
        if body is None or attachment_path is None:
            raise ValueError("body and attachment_path must be provided together.")
        return _build_attachment_message(sender, recipients, subject, body, attachment_path)

    raise ValueError("Missing email body payload.")
