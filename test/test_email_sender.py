from pathlib import Path
import pytest
from carlo_bot.infrastructure.email.builder import build_email_message
from carlo_bot.infrastructure.storage.models import PhotoAsset


def test_build_email_message_creates_message_with_attachment(tmp_path: Path):
    image_file = tmp_path / "carlo.jpg"
    image_file.write_bytes(b"fake-image-bytes")

    message = build_email_message(
        sender="bot@example.com",
        recipients=["alice@example.com", "bob@example.com"],
        subject="Test subject",
        body="Test body",
        attachment_path=image_file,
    )

    assert message["Subject"] == "Test subject"
    assert message["From"] == "bot@example.com"
    assert message["To"] == "alice@example.com, bob@example.com"
    assert message.get_body(preferencelist=("plain",)).get_content().strip() == "Test body"

    attachments = list(message.iter_attachments())
    assert len(attachments) == 1
    assert attachments[0].get_filename() == "carlo.jpg"


def test_build_email_message_raises_if_recipients_are_empty(tmp_path: Path):
    image_file = tmp_path / "carlo.jpg"
    image_file.write_bytes(b"fake-image-bytes")

    with pytest.raises(ValueError, match="Recipients list cannot be empty"):
        build_email_message(
            sender="bot@example.com",
            recipients=[],
            subject="Test subject",
            body="Test body",
            attachment_path=image_file,
        )


def test_build_email_message_raises_if_attachment_is_missing(tmp_path: Path):
    missing_file = tmp_path / "missing.jpg"

    with pytest.raises(FileNotFoundError, match="Attachment file not found"):
        build_email_message(
            sender="bot@example.com",
            recipients=["alice@example.com"],
            subject="Test subject",
            body="Test body",
            attachment_path=missing_file,
        )


def test_build_email_message_creates_inline_message_from_photo_asset():
    message = build_email_message(
        sender="bot@example.com",
        recipients=["alice@example.com"],
        subject="Test subject",
        plain_body="Plain body",
        html_body="<p>Html body</p>",
        image_asset=PhotoAsset(name="carlo.jpg", content_bytes=b"fake-image-bytes", mime_type="image/jpeg"),
    )

    html_body = message.get_body(preferencelist=("html",))

    assert message.get_body(preferencelist=("plain",)).get_content().strip() == "Plain body"
    assert html_body is not None
    assert any(part.get_filename() == "carlo.jpg" for part in message.walk())
