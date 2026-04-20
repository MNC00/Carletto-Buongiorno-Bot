import random
from pathlib import Path


def pick_active_contacts(contacts: list[dict]) -> list[dict]:
    # Filters contacts to those with active=True; raises if no active contact exists
    active_contacts = [contact for contact in contacts if contact["active"] is True]

    if not active_contacts:
        raise ValueError("No active contacts found.")

    return active_contacts


def pick_random_quote(quotes: list[str]) -> str:
    # Randomly selects one quote from the list using uniform distribution
    if not quotes:
        raise ValueError("Quotes list is empty.")

    return random.choice(quotes)


def pick_random_photo(photo_paths: list[Path]) -> Path:
    # Randomly selects one photo path from the list using uniform distribution
    if not photo_paths:
        raise ValueError("Photo paths list is empty.")

    return random.choice(photo_paths)


def pick_random_saint(saints: list[str]) -> str:
    # Randomly selects one saint entry from the list using uniform distribution
    if not saints:
        raise ValueError("Saints list is empty.")

    return random.choice(saints)


def pick_random_blasfemia(blasfemie: list[str]) -> str:
    # Randomly selects one blasfemia entry from the list using uniform distribution
    if not blasfemie:
        raise ValueError("Blasfemie list is empty.")

    return random.choice(blasfemie)
