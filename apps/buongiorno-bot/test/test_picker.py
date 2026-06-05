from datetime import date
from pathlib import Path
import pytest

from carlo_bot.domain.picker import (
    pick_active_contacts,
    pick_birthday_contacts,
    pick_random_photo,
    pick_random_quote,
)


def test_pick_active_contacts_returns_only_active_contacts():
    contacts = [
        {"name": "Mario", "email": "mario@example.com", "active": True},
        {"name": "Giulia", "email": "giulia@example.com", "active": False},
        {"name": "Luca", "email": "luca@example.com", "active": True},
    ]

    result = pick_active_contacts(contacts)

    assert len(result) == 2
    assert result == [
        {"name": "Mario", "email": "mario@example.com", "active": True},
        {"name": "Luca", "email": "luca@example.com", "active": True},
    ]


def test_pick_active_contacts_raises_if_no_active_contacts():
    contacts = [
        {"name": "Giulia", "email": "giulia@example.com", "active": False},
    ]

    with pytest.raises(ValueError, match="No active contacts found"):
        pick_active_contacts(contacts)


def test_pick_random_quote_returns_one_of_input_quotes():
    quotes = ["ciao", "buongiorno", "forza Carlo"]

    result = pick_random_quote(quotes)

    assert result in quotes


def test_pick_random_quote_raises_if_list_is_empty():
    with pytest.raises(ValueError, match="Quotes list is empty"):
        pick_random_quote([])


def test_pick_random_photo_returns_one_of_input_paths():
    photos = [
        Path("carlo_1.jpg"),
        Path("carlo_2.jpg"),
        Path("carlo_3.png"),
    ]

    result = pick_random_photo(photos)

    assert result in photos


def test_pick_random_photo_raises_if_list_is_empty():
    with pytest.raises(ValueError, match="Photo paths list is empty"):
        pick_random_photo([])


def test_pick_random_quote_can_be_made_predictable(monkeypatch):
    quotes = ["q1", "q2", "q3"]

    monkeypatch.setattr("carlo_bot.domain.picker.random.choice", lambda items: items[0])

    result = pick_random_quote(quotes)

    assert result == "q1"


def test_pick_birthday_contacts_returns_contacts_with_birthday_today():
    today = date(2026, 6, 5)
    contacts = [
        {"name": "Mario", "email": "mario@example.com", "active": True, "data_di_nascita": (6, 5)},
        {"name": "Giulia", "email": "giulia@example.com", "active": True, "data_di_nascita": (6, 6)},
        {"name": "Luca", "email": "luca@example.com", "active": True, "data_di_nascita": (6, 5)},
    ]

    result = pick_birthday_contacts(contacts, today=today)

    assert len(result) == 2
    assert result[0]["name"] == "Mario"
    assert result[1]["name"] == "Luca"


def test_pick_birthday_contacts_excludes_contacts_without_date():
    today = date(2026, 6, 5)
    contacts = [
        {"name": "Mario", "email": "mario@example.com", "active": True, "data_di_nascita": None},
        {"name": "Giulia", "email": "giulia@example.com", "active": True},
    ]

    result = pick_birthday_contacts(contacts, today=today)

    assert result == []


def test_pick_birthday_contacts_excludes_wrong_day():
    today = date(2026, 6, 5)
    contacts = [
        {"name": "Mario", "email": "mario@example.com", "active": True, "data_di_nascita": (6, 6)},
    ]

    result = pick_birthday_contacts(contacts, today=today)

    assert result == []


def test_pick_birthday_contacts_handles_leap_year_feb_29():
    today = date(2024, 2, 29)
    contacts = [
        {"name": "Mario", "email": "mario@example.com", "active": True, "data_di_nascita": (2, 29)},
        {"name": "Giulia", "email": "giulia@example.com", "active": True, "data_di_nascita": (2, 28)},
    ]

    result = pick_birthday_contacts(contacts, today=today)

    assert len(result) == 1
    assert result[0]["name"] == "Mario"


def test_pick_birthday_contacts_returns_empty_when_no_birthdays():
    today = date(2026, 1, 1)
    contacts = [
        {"name": "Mario", "email": "mario@example.com", "active": True, "data_di_nascita": (6, 5)},
    ]

    result = pick_birthday_contacts(contacts, today=today)

    assert result == []
