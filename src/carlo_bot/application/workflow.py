from carlo_bot.bootstrap.runtime import build_paths, get_project_root
from carlo_bot.domain.composer import build_html_body, build_plain_body, build_subject
from carlo_bot.domain.loaders import load_blasfemie, load_contacts, load_photo_paths, load_quotes, load_saints
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


def run_workflow(config: AppConfig, dry_run: bool) -> None:
    project_root = get_project_root()
    contacts_path, quotes_path, photos_path, saints_path, blasfemie_path = build_paths(project_root, config)

    contacts = load_contacts(contacts_path)
    quotes = load_quotes(quotes_path)
    photo_paths = load_photo_paths(photos_path)
    saints = load_saints(saints_path)
    blasfemie = load_blasfemie(blasfemie_path)

    active_contacts = pick_active_contacts(contacts)
    selected_quote = pick_random_quote(quotes)
    selected_photo = pick_random_photo(photo_paths)
    selected_saint = pick_random_saint(saints)
    selected_blasfemia = pick_random_blasfemia(blasfemie)

    subject = build_subject()
    plain_body = build_plain_body(selected_quote, selected_saint, selected_blasfemia)
    html_body = build_html_body(selected_quote, selected_saint, selected_blasfemia)
    recipients = [contact["email"] for contact in active_contacts]

    message = build_email_message(
        sender=config.smtp_sender,
        recipients=recipients,
        subject=subject,
        plain_body=plain_body,
        html_body=html_body,
        image_path=selected_photo,
    )

    print("=== Configuration ===")
    print(f"Environment: {config.app_env}")
    print(f"Dry run: {dry_run}")

    print("\n=== Loading summary ===")
    print(f"Contacts loaded: {len(contacts)}")
    print(f"Active contacts: {len(active_contacts)}")
    print(f"Quotes loaded: {len(quotes)}")
    print(f"Photos loaded: {len(photo_paths)}")

    print("\n=== Selection result ===")
    print(f"Selected quote: {selected_quote}")
    print(f"Selected saint: {selected_saint}")
    print(f"Selected blasfemia: {selected_blasfemia}")
    print(f"Selected photo: {selected_photo.name}")

    print("\n=== Composed email ===")
    print(f"Subject: {subject}")
    print(f"Recipients: {recipients}")
    print(f"Inline image: {selected_photo.name}")

    if dry_run:
        print("\nDRY_RUN enabled: email not sent.")
        return

    send_email(config, message)
    print("\nEmail sent successfully.")
