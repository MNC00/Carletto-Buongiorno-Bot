from argparse import Namespace
from pathlib import Path

from carlo_bot.infrastructure.config import AppConfig


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_paths(project_root: Path, config: AppConfig) -> tuple[Path, Path, Path, Path, Path]:
    contacts_path = project_root / config.contacts_file
    quotes_path = project_root / config.quotes_file
    photos_path = project_root / config.photos_dir
    saints_path = project_root / config.saints_file
    blasfemie_path = project_root / config.blasfemie_file
    return contacts_path, quotes_path, photos_path, saints_path, blasfemie_path


def resolve_dry_run(config: AppConfig, args: Namespace) -> bool:
    if args.send and args.dry_run:
        raise ValueError("Usa solo uno tra --send e --dry-run.")

    if args.send:
        return False

    if args.dry_run:
        return True

    return config.dry_run
