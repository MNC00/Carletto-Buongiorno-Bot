from datetime import date
from types import SimpleNamespace

from carlo_bot.application.workflow import run_workflow
from carlo_bot.infrastructure.storage.models import PhotoAsset


class FakeStorageProvider:
    def __init__(self, contacts=None):
        self._contacts = contacts or [
            {"name": "Alice", "email": "alice@example.com", "active": True},
            {"name": "Bob", "email": "bob@example.com", "active": True},
        ]

    def load_contacts(self) -> list[dict]:
        return self._contacts

    def load_quotes(self) -> list[str]:
        return ["Quote of the day"]

    def load_photo_assets(self) -> list[PhotoAsset]:
        return [PhotoAsset(name="carlo.jpg", content_bytes=b"fake-image-bytes", mime_type="image/jpeg")]

    def load_saints(self) -> list[str]:
        return ["San Gennaro"]

    def load_blasfemie(self) -> list[str]:
        return ["culone"]


def test_run_workflow_sends_one_message_per_active_contact(monkeypatch):
    config = SimpleNamespace(
        app_env="test",
        smtp_sender="bot@example.com",
        unsubscribe_base_url="https://example.com/unsubscribe",
        unsubscribe_secret="super-secret",
        gemini_api_key=None,
        llm_prompt_file="",
        birthday_prompt_file="",
    )
    built_messages: list[tuple[str, list[str], str, str]] = []
    sent_recipients: list[str] = []

    monkeypatch.setattr(
        "carlo_bot.application.workflow.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(),
    )

    def fake_build_email_message(*, sender, recipients, subject, plain_body, html_body, image_asset):
        built_messages.append((sender, recipients, plain_body, html_body))
        return {"sender": sender, "recipients": recipients, "subject": subject}

    monkeypatch.setattr("carlo_bot.application.workflow.build_email_message", fake_build_email_message)
    monkeypatch.setattr(
        "carlo_bot.application.workflow.send_email",
        lambda config, message: sent_recipients.extend(message["recipients"]),
    )

    run_workflow(config=config, dry_run=False)

    assert built_messages[0][0:2] == ("bot@example.com", ["alice@example.com"])
    assert built_messages[1][0:2] == ("bot@example.com", ["bob@example.com"])
    assert built_messages[0][2].startswith("Buongiorno Alice!")
    assert built_messages[1][2].startswith("Buongiorno Bob!")
    assert "<p>Buongiorno Alice!</p>" in built_messages[0][3]
    assert "https://example.com/unsubscribe?email=alice%40example.com&sig=" in built_messages[0][2]
    assert "https://example.com/unsubscribe?email=bob%40example.com&sig=" in built_messages[1][2]
    assert "href=\"https://example.com/unsubscribe?email=alice%40example.com&amp;sig=" in built_messages[0][3]
    assert sent_recipients == ["alice@example.com", "bob@example.com"]


def test_run_workflow_dry_run_builds_one_message_per_active_contact_without_sending(monkeypatch):
    config = SimpleNamespace(
        app_env="test",
        smtp_sender="bot@example.com",
        unsubscribe_base_url=None,
        unsubscribe_secret=None,
        gemini_api_key=None,
        llm_prompt_file="",
        birthday_prompt_file="",
    )
    built_recipients: list[tuple[list[str], str]] = []
    send_calls = 0

    monkeypatch.setattr(
        "carlo_bot.application.workflow.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(),
    )

    def fake_build_email_message(*, sender, recipients, subject, plain_body, html_body, image_asset):
        built_recipients.append((recipients, plain_body))
        return {"sender": sender, "recipients": recipients, "subject": subject}

    def fake_send_email(config, message):
        nonlocal send_calls
        send_calls += 1

    monkeypatch.setattr("carlo_bot.application.workflow.build_email_message", fake_build_email_message)
    monkeypatch.setattr("carlo_bot.application.workflow.send_email", fake_send_email)

    run_workflow(config=config, dry_run=True)

    assert built_recipients == [(["alice@example.com"], built_recipients[0][1]), (["bob@example.com"], built_recipients[1][1])]
    assert built_recipients[0][1].startswith("Buongiorno Alice!")
    assert built_recipients[1][1].startswith("Buongiorno Bob!")
    assert "Per non ricevere piu questa mail" not in built_recipients[0][1]
    assert send_calls == 0


def test_run_workflow_uses_nickname_in_greeting(monkeypatch):
    contacts = [
        {"name": "Alice", "email": "alice@example.com", "active": True, "nickname": "Ali"},
        {"name": "Bob", "email": "bob@example.com", "active": True, "nickname": None},
    ]
    config = SimpleNamespace(
        app_env="test",
        smtp_sender="bot@example.com",
        unsubscribe_base_url=None,
        unsubscribe_secret=None,
        gemini_api_key=None,
        llm_prompt_file="",
        birthday_prompt_file="",
    )
    built_messages: list[str] = []

    monkeypatch.setattr(
        "carlo_bot.application.workflow.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(contacts=contacts),
    )

    def fake_build_email_message(*, sender, recipients, subject, plain_body, html_body, image_asset):
        built_messages.append(plain_body)
        return {"sender": sender, "recipients": recipients, "subject": subject}

    monkeypatch.setattr("carlo_bot.application.workflow.build_email_message", fake_build_email_message)
    monkeypatch.setattr("carlo_bot.application.workflow.send_email", lambda config, message: None)

    run_workflow(config=config, dry_run=False)

    assert built_messages[0].startswith("Buongiorno Ali!")
    assert built_messages[1].startswith("Buongiorno Bob!")


def test_run_workflow_birthday_private_only_birthday_contact_gets_greeting(monkeypatch):
    today = date(2026, 6, 5)
    contacts = [
        {"name": "Alice", "cognome": "Rossi", "email": "alice@example.com", "active": True,
         "data_di_nascita": (6, 5), "birthday_public": False},
        {"name": "Bob", "email": "bob@example.com", "active": True,
         "data_di_nascita": None, "birthday_public": True},
    ]
    config = SimpleNamespace(
        app_env="test",
        smtp_sender="bot@example.com",
        unsubscribe_base_url=None,
        unsubscribe_secret=None,
        gemini_api_key=None,
        llm_prompt_file="",
        birthday_prompt_file="",
    )
    built_messages: list[tuple[list[str], str]] = []

    monkeypatch.setattr(
        "carlo_bot.application.workflow.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(contacts=contacts),
    )
    monkeypatch.setattr(
        "carlo_bot.application.workflow.pick_birthday_contacts",
        lambda contacts, **kw: [c for c in contacts if c.get("data_di_nascita") == (today.month, today.day)],
    )

    def fake_build_email_message(*, sender, recipients, subject, plain_body, html_body, image_asset):
        built_messages.append((recipients, plain_body))
        return {"sender": sender, "recipients": recipients, "subject": subject}

    monkeypatch.setattr("carlo_bot.application.workflow.build_email_message", fake_build_email_message)
    monkeypatch.setattr("carlo_bot.application.workflow.send_email", lambda config, message: None)

    run_workflow(config=config, dry_run=False)

    alice_body = built_messages[0][1]
    bob_body = built_messages[1][1]
    assert "\U0001F382" in alice_body
    assert "\U0001F382" not in bob_body


def test_run_workflow_birthday_public_all_contacts_see_greeting(monkeypatch):
    today = date(2026, 6, 5)
    contacts = [
        {"name": "Alice", "cognome": "Rossi", "email": "alice@example.com", "active": True,
         "data_di_nascita": (6, 5), "birthday_public": True},
        {"name": "Bob", "cognome": "Verdi", "email": "bob@example.com", "active": True,
         "data_di_nascita": None, "birthday_public": True},
    ]
    config = SimpleNamespace(
        app_env="test",
        smtp_sender="bot@example.com",
        unsubscribe_base_url=None,
        unsubscribe_secret=None,
        gemini_api_key=None,
        llm_prompt_file="",
        birthday_prompt_file="",
    )
    built_messages: list[tuple[list[str], str]] = []

    monkeypatch.setattr(
        "carlo_bot.application.workflow.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(contacts=contacts),
    )
    monkeypatch.setattr(
        "carlo_bot.application.workflow.pick_birthday_contacts",
        lambda contacts, **kw: [c for c in contacts if c.get("data_di_nascita") == (today.month, today.day)],
    )

    def fake_build_email_message(*, sender, recipients, subject, plain_body, html_body, image_asset):
        built_messages.append((recipients, plain_body))
        return {"sender": sender, "recipients": recipients, "subject": subject}

    monkeypatch.setattr("carlo_bot.application.workflow.build_email_message", fake_build_email_message)
    monkeypatch.setattr("carlo_bot.application.workflow.send_email", lambda config, message: None)

    run_workflow(config=config, dry_run=False)

    alice_body = built_messages[0][1]
    bob_body = built_messages[1][1]
    assert "\U0001F382" in alice_body
    assert "\U0001F382" in bob_body
    assert "Alice Rossi" in bob_body


def test_run_workflow_no_birthday_no_birthday_section(monkeypatch):
    contacts = [
        {"name": "Alice", "email": "alice@example.com", "active": True, "data_di_nascita": None},
    ]
    config = SimpleNamespace(
        app_env="test",
        smtp_sender="bot@example.com",
        unsubscribe_base_url=None,
        unsubscribe_secret=None,
        gemini_api_key=None,
        llm_prompt_file="",
        birthday_prompt_file="",
    )
    built_messages: list[str] = []

    monkeypatch.setattr(
        "carlo_bot.application.workflow.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(contacts=contacts),
    )

    def fake_build_email_message(*, sender, recipients, subject, plain_body, html_body, image_asset):
        built_messages.append(plain_body)
        return {"sender": sender, "recipients": recipients, "subject": subject}

    monkeypatch.setattr("carlo_bot.application.workflow.build_email_message", fake_build_email_message)
    monkeypatch.setattr("carlo_bot.application.workflow.send_email", lambda config, message: None)

    run_workflow(config=config, dry_run=False)

    assert "\U0001F382" not in built_messages[0]