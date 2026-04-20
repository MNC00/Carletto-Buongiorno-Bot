import json
from pathlib import Path

import pytest

from carlo_bot.domain.loaders import load_blasfemie, load_contacts, load_photo_paths, load_quotes, load_saints


def test_load_contacts_returns_list_of_contacts(tmp_path: Path):
    contacts_file = tmp_path / "contacts.json"
    contacts_data = [
        {"name": "Mario", "email": "mario@example.com", "active": True},
        {"name": "Giulia", "email": "giulia@example.com", "active": False},
    ]
    contacts_file.write_text(json.dumps(contacts_data), encoding="utf-8")

    result = load_contacts(contacts_file)

    assert len(result) == 2
    assert result[0]["name"] == "Mario"
    assert result[1]["active"] is False


def test_load_contacts_raises_if_file_is_missing(tmp_path: Path):
    missing_file = tmp_path / "missing_contacts.json"

    with pytest.raises(FileNotFoundError):
        load_contacts(missing_file)


def test_load_contacts_raises_if_required_field_is_missing(tmp_path: Path):
    contacts_file = tmp_path / "contacts.json"
    invalid_data = [
        {"name": "Mario", "active": True}
    ]
    contacts_file.write_text(json.dumps(invalid_data), encoding="utf-8")

    with pytest.raises(ValueError, match="missing fields"):
        load_contacts(contacts_file)


def test_load_quotes_returns_non_empty_lines(tmp_path: Path):
    quotes_file = tmp_path / "quotes.txt"
    quotes_file.write_text(
        "Prima citazione\n\nSeconda citazione\n   \nTerza citazione\n",
        encoding="utf-8",
    )

    result = load_quotes(quotes_file)

    assert result == [
        "Prima citazione",
        "Seconda citazione",
        "Terza citazione",
    ]


def test_load_quotes_raises_if_file_is_missing(tmp_path: Path):
    missing_file = tmp_path / "quotes.txt"

    with pytest.raises(FileNotFoundError):
        load_quotes(missing_file)


def test_load_photo_paths_returns_only_supported_images(tmp_path: Path):
    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()

    image_1 = photos_dir / "carlo_1.jpg"
    image_2 = photos_dir / "carlo_2.png"
    ignored_file = photos_dir / "notes.txt"

    image_1.write_text("fake image content", encoding="utf-8")
    image_2.write_text("fake image content", encoding="utf-8")
    ignored_file.write_text("not an image", encoding="utf-8")

    result = load_photo_paths(photos_dir)

    assert len(result) == 2
    assert image_1 in result
    assert image_2 in result
    assert ignored_file not in result


def test_load_photo_paths_raises_if_no_valid_images_found(tmp_path: Path):
    photos_dir = tmp_path / "photos"
    photos_dir.mkdir()

    file_1 = photos_dir / "readme.txt"
    file_1.write_text("hello", encoding="utf-8")

    with pytest.raises(ValueError, match="No valid image files found"):
        load_photo_paths(photos_dir)

def test_load_saints_returns_non_empty_lines(tmp_path: Path):
    saints_file = tmp_path / "saints.txt"
    saints_file.write_text(
        "San Giorgio\n\nSanta Lucia\n   \nSan Francesco\n",
        encoding="utf-8",
    )

    result = load_saints(saints_file)

    assert result == [
        "San Giorgio",
        "Santa Lucia",
        "San Francesco",
    ]


def test_load_saints_raises_if_file_is_missing(tmp_path: Path):
    missing_file = tmp_path / "saints.txt"

    with pytest.raises(FileNotFoundError):
        load_saints(missing_file)


def test_load_saints_raises_if_file_is_empty(tmp_path: Path):
    saints_file = tmp_path / "saints.txt"
    saints_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Saints file is empty"):
        load_saints(saints_file)


def test_load_blasfemie_returns_non_empty_lines(tmp_path: Path):
    blasfemie_file = tmp_path / "blasfemie.txt"
    blasfemie_file.write_text(
        "Blasfemia uno\n\nBlasfemia due\n   \nBlasfemia tre\n",
        encoding="utf-8",
    )

    result = load_blasfemie(blasfemie_file)

    assert result == [
        "Blasfemia uno",
        "Blasfemia due",
        "Blasfemia tre",
    ]


def test_load_blasfemie_raises_if_file_is_missing(tmp_path: Path):
    missing_file = tmp_path / "blasfemie.txt"

    with pytest.raises(FileNotFoundError):
        load_blasfemie(missing_file)


def test_load_blasfemie_raises_if_file_is_empty(tmp_path: Path):
    blasfemie_file = tmp_path / "blasfemie.txt"
    blasfemie_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Blasfemie file is empty"):
        load_blasfemie(blasfemie_file)
