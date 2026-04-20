from carlo_bot.agents.contracts import AgentTaskResult
from carlo_bot.domain.composer import build_html_body, build_plain_body, build_subject
from carlo_bot.domain.loaders import load_blasfemie, load_contacts, load_photo_paths, load_quotes, load_saints
from carlo_bot.domain.picker import (
    pick_active_contacts,
    pick_random_blasfemia,
    pick_random_photo,
    pick_random_quote,
    pick_random_saint,
)
from carlo_bot.infrastructure.email.builder import build_email_message
from carlo_bot.infrastructure.email.sender import send_email


def load_inputs(*, contacts_path, quotes_path, photos_path, saints_path, blasfemie_path) -> AgentTaskResult:
    payload = {
        "contacts": load_contacts(contacts_path),
        "quotes": load_quotes(quotes_path),
        "photo_paths": load_photo_paths(photos_path),
        "saints": load_saints(saints_path),
        "blasfemie": load_blasfemie(blasfemie_path),
    }
    return AgentTaskResult(name="load_inputs", payload=payload)


def select_content(*, contacts, quotes, photo_paths, saints, blasfemie) -> AgentTaskResult:
    payload = {
        "active_contacts": pick_active_contacts(contacts),
        "selected_quote": pick_random_quote(quotes),
        "selected_photo": pick_random_photo(photo_paths),
        "selected_saint": pick_random_saint(saints),
        "selected_blasfemia": pick_random_blasfemia(blasfemie),
    }
    return AgentTaskResult(name="select_content", payload=payload)


def compose_message(*, quote, saint, blasfemia) -> AgentTaskResult:
    payload = {
        "subject": build_subject(),
        "plain_body": build_plain_body(quote, saint, blasfemia),
        "html_body": build_html_body(quote, saint, blasfemia),
    }
    return AgentTaskResult(name="compose_message", payload=payload)


def build_email(*, sender, recipients, subject, plain_body, html_body, image_path) -> AgentTaskResult:
    message = build_email_message(
        sender=sender,
        recipients=recipients,
        subject=subject,
        plain_body=plain_body,
        html_body=html_body,
        image_path=image_path,
    )
    return AgentTaskResult(name="build_email", payload=message)


def dispatch_email(*, config, message) -> AgentTaskResult:
    send_email(config, message)
    return AgentTaskResult(name="send_email", payload=None)
