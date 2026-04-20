# Entry point: imports and delegates execution to the CLI handler when run as a script
from carlo_bot.bootstrap.cli import main


if __name__ == "__main__":
    main()