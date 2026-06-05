from email.message import EmailMessage
from html import escape
from pathlib import Path

from carlo_bot.bootstrap.runtime import get_project_root
from carlo_bot.domain.picker import pick_active_contacts
from carlo_bot.infrastructure.config import AppConfig
from carlo_bot.infrastructure.email.builder import INLINE_IMAGE_CID, build_email_message
from carlo_bot.infrastructure.email.sender import send_email
from carlo_bot.infrastructure.storage import build_storage_provider


DEFAULT_ANNOUNCEMENT_IMAGE = "packages/branding/SuperCarlo.jpg"


def run_announcement(
    *,
    config: AppConfig,
    dry_run: bool,
    subject: str,
    body: str,
    image_file: str = DEFAULT_ANNOUNCEMENT_IMAGE,
) -> None:
    if not subject or not subject.strip():
        raise ValueError("subject cannot be empty.")
    if not body or not body.strip():
        raise ValueError("body cannot be empty.")

    project_root = get_project_root()
    storage_provider = build_storage_provider(config=config, project_root=project_root)
    contacts = storage_provider.load_contacts()
    active_contacts = pick_active_contacts(contacts)
    image_path = _resolve_optional_image(project_root, image_file)

    print("=== Announcement ===")
    print(f"Dry run: {dry_run}")
    print(f"Subject: {subject.strip()}")
    print(f"Contacts loaded: {len(contacts)}")
    print(f"Active recipients: {len(active_contacts)}")
    if image_path is None:
        print(f"Image missing, sending without image: {project_root / image_file}")
    else:
        print(f"Image: {image_path}")

    preview_body: str | None = None
    preview_recipient: str | None = None

    for contact in active_contacts:
        recipient = contact["email"]
        plain_body = build_announcement_plain_body(contact=contact, body=body)
        html_body = build_announcement_html_body(contact=contact, body=body, include_image=image_path is not None)
        message = _build_announcement_message(
            sender=config.smtp_sender,
            recipient=recipient,
            subject=subject.strip(),
            plain_body=plain_body,
            html_body=html_body,
            image_path=image_path,
        )

        if dry_run:
            print(f"Prepared announcement for: {recipient}")
            if preview_body is None:
                preview_body = plain_body
                preview_recipient = recipient
            continue

        send_email(config, message)
        print(f"Announcement sent to: {recipient}")

    if dry_run:
        if preview_body is not None:
            print(f"\n=== Plain text announcement preview (to {preview_recipient}) ===")
            print(preview_body)
            print("=== End plain text announcement preview ===")
        print("\nDRY_RUN enabled: announcements not sent.")
        return

    print("\nAnnouncements sent successfully.")


def build_announcement_plain_body(*, contact: dict, body: str) -> str:
    return f"Ciao {_display_name(contact)},\n\n{body.strip()}"


def build_announcement_html_body(*, contact: dict, body: str, include_image: bool) -> str:
    display_name = escape(_display_name(contact))
    body_html = _paragraphs_to_html(body)
    image_html = ""
    if include_image:
        image_html = (
            f'\n        <p><img src="cid:{INLINE_IMAGE_CID}" alt="SuperCarlo" '
            'style="max-width: 320px; height: auto;"></p>'
        )

    return f"""
    <html>
      <body>
        <p>Ciao {display_name},</p>
{body_html}{image_html}
      </body>
    </html>
    """.strip()


def _display_name(contact: dict) -> str:
    for key in ("nickname", "name"):
        value = contact.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return "amico mio"


def _paragraphs_to_html(body: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in body.strip().split("\n\n") if paragraph.strip()]
    html_paragraphs = []
    for paragraph in paragraphs:
        safe_paragraph = escape(paragraph).replace("\n", "<br>")
        html_paragraphs.append(f"        <p>{safe_paragraph}</p>")
    return "\n".join(html_paragraphs)


def _resolve_optional_image(project_root: Path, image_file: str) -> Path | None:
    image_path = Path(image_file)
    if not image_path.is_absolute():
        image_path = project_root / image_path

    if not image_path.exists():
        return None

    return image_path


def _build_announcement_message(
    *,
    sender: str,
    recipient: str,
    subject: str,
    plain_body: str,
    html_body: str,
    image_path: Path | None,
) -> EmailMessage:
    if image_path is not None:
        return build_email_message(
            sender=sender,
            recipients=[recipient],
            subject=subject,
            plain_body=plain_body,
            html_body=html_body,
            image_path=image_path,
        )

    return _build_plain_html_message(
        sender=sender,
        recipient=recipient,
        subject=subject,
        plain_body=plain_body,
        html_body=html_body,
    )


def _build_plain_html_message(
    *,
    sender: str,
    recipient: str,
    subject: str,
    plain_body: str,
    html_body: str,
) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.set_content(plain_body)
    message.add_alternative(html_body, subtype="html")
    return message