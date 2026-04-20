from carlo_bot.domain.composer import build_html_body, build_plain_body, build_subject
from carlo_bot.bootstrap.runtime import get_project_root
from carlo_bot.domain.picker import (
    pick_active_contacts,
    pick_random_blasfemia,
    pick_random_photo,
    pick_random_quote,
    pick_random_saint,
)
from carlo_bot.infrastructure.config import AppConfig
from carlo_bot.infrastructure.email.builder import build_email_message
from carlo_bot.infrastructure.email.sender import send_email
from carlo_bot.infrastructure.storage import build_storage_provider


def run_workflow(config: AppConfig, dry_run: bool) -> None:
    # Instantiates the storage provider (filesystem or Google Workspace) based on STORAGE_BACKEND
    project_root = get_project_root()
    storage_provider = build_storage_provider(config=config, project_root=project_root)

    # Loads all datasets from the configured backend in one pass
    contacts = storage_provider.load_contacts()
    quotes = storage_provider.load_quotes()
    photo_assets = storage_provider.load_photo_assets()
    saints = storage_provider.load_saints()
    blasfemie = storage_provider.load_blasfemie()

    # Filters contacts to active-only and picks one random item from each content dataset
    active_contacts = pick_active_contacts(contacts)
    selected_quote = pick_random_quote(quotes)
    selected_photo = pick_random_photo(photo_assets)
    selected_saint = pick_random_saint(saints)
    selected_blasfemia = pick_random_blasfemia(blasfemie)

    # Builds email subject, plain-text body, and HTML body from the selected content
    subject = build_subject()
    plain_body = build_plain_body(selected_quote, selected_saint, selected_blasfemia)
    html_body = build_html_body(selected_quote, selected_saint, selected_blasfemia)
    recipients = [contact["email"] for contact in active_contacts]

    # Assembles the full MIME email with the photo embedded inline via Content-ID
    message = build_email_message(
        sender=config.smtp_sender,
        recipients=recipients,
        subject=subject,
        plain_body=plain_body,
        html_body=html_body,
        image_asset=selected_photo,
    )

    # Prints a structured summary of configuration, loaded data, selections, and email details
    print("=== Configuration ===")
    print(f"Environment: {config.app_env}")
    print(f"Dry run: {dry_run}")

    print("\n=== Loading summary ===")
    print(f"Contacts loaded: {len(contacts)}")
    print(f"Active contacts: {len(active_contacts)}")
    print(f"Quotes loaded: {len(quotes)}")
    print(f"Photos loaded: {len(photo_assets)}")

    print("\n=== Selection result ===")
    print(f"Selected quote: {selected_quote}")
    print(f"Selected saint: {selected_saint}")
    print(f"Selected blasfemia: {selected_blasfemia}")
    print(f"Selected photo: {selected_photo.name}")

    print("\n=== Composed email ===")
    print(f"Subject: {subject}")
    print(f"Recipients: {recipients}")
    print(f"Inline image: {selected_photo.name}")

    # Skips SMTP delivery if dry_run is active; otherwise sends the message via SMTP_SSL
    if dry_run:
        print("\nDRY_RUN enabled: email not sent.")
        return

    send_email(config, message)
    print("\nEmail sent successfully.")
