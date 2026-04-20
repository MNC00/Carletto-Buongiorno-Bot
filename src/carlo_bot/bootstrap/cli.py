import argparse

from carlo_bot.application.workflow import run_workflow
from carlo_bot.bootstrap.runtime import resolve_dry_run
from carlo_bot.infrastructure.config import load_config


def parse_args() -> argparse.Namespace:
    # Defines CLI flags: --send forces real email delivery, --dry-run forces simulation only
    parser = argparse.ArgumentParser(description="Carlo Random Good Morning Bot")
    parser.add_argument(
        "--send",
        action="store_true",
        help="Invia davvero la mail, ignorando DRY_RUN=true nel .env",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Forza dry run, senza inviare la mail",
    )
    return parser.parse_args()


def main() -> None:
    # Loads config from .env, parses CLI args, resolves dry_run mode, then runs the full workflow
    config = load_config()
    args = parse_args()
    dry_run = resolve_dry_run(config, args)
    run_workflow(config=config, dry_run=dry_run)
