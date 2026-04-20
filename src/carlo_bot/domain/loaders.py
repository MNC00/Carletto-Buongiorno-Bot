import json
from pathlib import Path

ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def load_contacts(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Contacts file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise ValueError("Contacts JSON must contain a list of contacts.")

    contacts = []
    for index, contact in enumerate(data):
        if not isinstance(contact, dict):
            raise ValueError(f"Contact at index {index} is not a JSON object.")

        required_fields = {"name", "email", "active"}
        missing_fields = required_fields - contact.keys()
        if missing_fields:
            raise ValueError(
                f"Contact at index {index} is missing fields: {sorted(missing_fields)}"
            )

        if not isinstance(contact["name"], str) or not contact["name"].strip():
            raise ValueError(f"Contact at index {index} has invalid 'name'.")

        if not isinstance(contact["email"], str) or not contact["email"].strip():
            raise ValueError(f"Contact at index {index} has invalid 'email'.")

        if not isinstance(contact["active"], bool):
            raise ValueError(f"Contact at index {index} has invalid 'active'.")

        contacts.append(contact)

    if not contacts:
        raise ValueError("Contacts JSON is empty.")

    return contacts


def load_quotes(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Quotes file not found: {path}")

    quotes = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not quotes:
        raise ValueError("Quotes file is empty.")

    return quotes


def load_photo_paths(path: Path) -> list[Path]:
    if not path.exists():
        raise FileNotFoundError(f"Photos directory not found: {path}")

    if not path.is_dir():
        raise ValueError(f"Photos path is not a directory: {path}")

    photo_paths = [
        item
        for item in path.iterdir()
        if item.is_file() and item.suffix.lower() in ALLOWED_IMAGE_SUFFIXES
    ]

    if not photo_paths:
        raise ValueError(
            f"No valid image files found in {path}. "
            f"Allowed extensions: {sorted(ALLOWED_IMAGE_SUFFIXES)}"
        )

    return photo_paths


def load_saints(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Saints file not found: {path}")

    saints = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not saints:
        raise ValueError("Saints file is empty.")

    return saints


def load_blasfemie(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Blasfemie file not found: {path}")

    blasfemie = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not blasfemie:
        raise ValueError("Blasfemie file is empty.")

    return blasfemie
