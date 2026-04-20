import mimetypes
from email.message import EmailMessage
from pathlib import Path


INLINE_IMAGE_CID = "carlo_photo"


def _build_inline_message(
    sender: str,
    recipients: list[str],
    subject: str,
    plain_body: str,
    html_body: str,
    image_path: Path,
) -> EmailMessage:
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)

    message.set_content(plain_body)
    message.add_alternative(html_body, subtype="html")

    mime_type, _ = mimetypes.guess_type(image_path.name)
    if mime_type is None:
        mime_type = "application/octet-stream"

    maintype, subtype = mime_type.split("/", 1)

    with open(image_path, "rb") as file:
        image_data = file.read()

    html_part = message.get_payload()[-1]
    html_part.add_related(
        image_data,
        maintype=maintype,
        subtype=subtype,
        cid=f"<{INLINE_IMAGE_CID}>",
        filename=image_path.name,
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
    *,
    body: str | None = None,
    attachment_path: Path | None = None,
) -> EmailMessage:
    if not recipients:
        raise ValueError("Recipients list cannot be empty.")

    if plain_body is not None or html_body is not None or image_path is not None:
        if plain_body is None or html_body is None or image_path is None:
            raise ValueError("plain_body, html_body, and image_path must be provided together.")
        return _build_inline_message(sender, recipients, subject, plain_body, html_body, image_path)

    if body is not None or attachment_path is not None:
        if body is None or attachment_path is None:
            raise ValueError("body and attachment_path must be provided together.")
        return _build_attachment_message(sender, recipients, subject, body, attachment_path)

    raise ValueError("Missing email body payload.")
