import argparse
from pathlib import Path

from carlo_bot.application.announcement import DEFAULT_ANNOUNCEMENT_IMAGE, run_announcement
from carlo_bot.bootstrap.runtime import get_project_root, resolve_dry_run
from carlo_bot.infrastructure.config import load_config


DEFAULT_BODY_FILE = "apps/buongiorno-bot/data/announcements/birthdate_request.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a generic announcement to active subscribers")
    parser.add_argument("--subject", required=True, help="Oggetto della mail")
    body_group = parser.add_mutually_exclusive_group()
    body_group.add_argument("--body", help="Corpo della mail in plain text")
    body_group.add_argument(
        "--body-file",
        default=DEFAULT_BODY_FILE,
        help=f"File di testo da usare come corpo della mail. Default: {DEFAULT_BODY_FILE}",
    )
    parser.add_argument(
        "--image-file",
        default=DEFAULT_ANNOUNCEMENT_IMAGE,
        help="Immagine inline opzionale. Default: packages/branding/SuperCarlo.jpg",
    )
    parser.add_argument("--send", action="store_true", help="Invia davvero la mail")
    parser.add_argument("--dry-run", action="store_true", help="Prepara la mail senza inviare")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    dry_run = resolve_dry_run(config, args)
    body = args.body if args.body is not None else _read_body_file(args.body_file)
    run_announcement(
        config=config,
        dry_run=dry_run,
        subject=args.subject,
        body=body,
        image_file=args.image_file,
    )


def _read_body_file(body_file: str) -> str:
    body_path = Path(body_file)
    if not body_path.is_absolute():
        body_path = get_project_root() / body_path
    return body_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    main()