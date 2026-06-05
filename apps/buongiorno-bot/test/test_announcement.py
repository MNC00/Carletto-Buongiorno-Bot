import importlib.util
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace

from carlo_bot.application.announcement import (
    build_announcement_html_body,
    build_announcement_plain_body,
    run_announcement,
)


def _load_send_announcement_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "send_announcement.py"
    spec = importlib.util.spec_from_file_location("send_announcement", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeStorageProvider:
    def __init__(self, contacts: list[dict]) -> None:
        self._contacts = contacts

    def load_contacts(self) -> list[dict]:
        return self._contacts

    def load_quotes(self) -> list[str]:
        return []

    def load_saints(self) -> list[str]:
        return []

    def load_blasfemie(self) -> list[str]:
        return []

    def load_photo_assets(self) -> list:
        return []


def _config() -> SimpleNamespace:
    return SimpleNamespace(
        app_env="test",
        smtp_sender="bot@example.com",
        storage_backend="filesystem",
    )


def _message(sender: str, recipients: list[str], subject: str) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content("placeholder")
    return message


def test_announcement_plain_body_uses_nickname():
    result = build_announcement_plain_body(contact={"name": "Alice", "nickname": "Ali"}, body="Testo iniziativa")

    assert result == "Ciao Ali,\n\nTesto iniziativa"


def test_announcement_plain_body_falls_back_to_name():
    result = build_announcement_plain_body(contact={"name": "Alice", "nickname": ""}, body="Testo iniziativa")

    assert result.startswith("Ciao Alice,")


def test_announcement_html_body_escapes_content_and_adds_image_when_requested():
    result = build_announcement_html_body(
        contact={"nickname": "<Ali>"},
        body="Prima riga\nSeconda <riga>",
        include_image=True,
    )

    assert "&lt;Ali&gt;" in result
    assert "Seconda &lt;riga&gt;" in result
    assert "cid:carlo_photo" in result
    assert "<Ali>" not in result


def test_announcement_sends_only_to_active_contacts_without_image(monkeypatch, tmp_path):
    contacts = [
        {"name": "Alice", "nickname": "Ali", "email": "alice@example.com", "active": True},
        {"name": "Bob", "nickname": "Bobby", "email": "bob@example.com", "active": False},
    ]
    sent_messages: list[EmailMessage] = []

    monkeypatch.setattr("carlo_bot.application.announcement.get_project_root", lambda: tmp_path)
    monkeypatch.setattr(
        "carlo_bot.application.announcement.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(contacts),
    )
    monkeypatch.setattr(
        "carlo_bot.application.announcement.send_email",
        lambda config, message: sent_messages.append(message),
    )

    run_announcement(config=_config(), dry_run=False, subject="Oggetto", body="Testo iniziativa")

    assert len(sent_messages) == 1
    message = sent_messages[0]
    assert message["To"] == "alice@example.com"
    assert message["Subject"] == "Oggetto"
    assert message.get_body(("plain",)).get_content().startswith("Ciao Ali,")


def test_announcement_uses_supercarlo_when_image_exists(monkeypatch, tmp_path):
    contacts = [{"name": "Alice", "email": "alice@example.com", "active": True}]
    image_path = tmp_path / "packages" / "branding" / "SuperCarlo.jpg"
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"fake-image")
    build_calls: list[dict] = []
    sent_messages: list[EmailMessage] = []

    monkeypatch.setattr("carlo_bot.application.announcement.get_project_root", lambda: tmp_path)
    monkeypatch.setattr(
        "carlo_bot.application.announcement.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(contacts),
    )

    def fake_build_email_message(**kwargs):
        build_calls.append(kwargs)
        return _message(kwargs["sender"], kwargs["recipients"], kwargs["subject"])

    monkeypatch.setattr("carlo_bot.application.announcement.build_email_message", fake_build_email_message)
    monkeypatch.setattr(
        "carlo_bot.application.announcement.send_email",
        lambda config, message: sent_messages.append(message),
    )

    run_announcement(config=_config(), dry_run=False, subject="Oggetto", body="Testo iniziativa")

    assert build_calls[0]["image_path"] == image_path
    assert "cid:carlo_photo" in build_calls[0]["html_body"]
    assert sent_messages[0]["To"] == "alice@example.com"


def test_announcement_dry_run_prints_preview_without_sending(monkeypatch, tmp_path, capsys):
    contacts = [{"name": "Alice", "nickname": "Ali", "email": "alice@example.com", "active": True}]
    send_calls = 0

    monkeypatch.setattr("carlo_bot.application.announcement.get_project_root", lambda: tmp_path)
    monkeypatch.setattr(
        "carlo_bot.application.announcement.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(contacts),
    )

    def fake_send_email(config, message):
        nonlocal send_calls
        send_calls += 1

    monkeypatch.setattr("carlo_bot.application.announcement.send_email", fake_send_email)

    run_announcement(config=_config(), dry_run=True, subject="Oggetto", body="Testo iniziativa")

    output = capsys.readouterr().out
    assert "Prepared announcement for: alice@example.com" in output
    assert "=== Plain text announcement preview (to alice@example.com) ===" in output
    assert "Ciao Ali," in output
    assert "Testo iniziativa" in output
    assert "DRY_RUN enabled: announcements not sent." in output
    assert send_calls == 0


def test_send_announcement_reads_body_file_relative_to_project_root(monkeypatch, tmp_path):
    module = _load_send_announcement_module()
    body_file = tmp_path / "apps" / "buongiorno-bot" / "data" / "announcements" / "body.txt"
    body_file.parent.mkdir(parents=True)
    body_file.write_text("Corpo modificabile", encoding="utf-8")

    monkeypatch.setattr(module, "get_project_root", lambda: tmp_path)

    result = module._read_body_file("apps/buongiorno-bot/data/announcements/body.txt")

    assert result == "Corpo modificabile"