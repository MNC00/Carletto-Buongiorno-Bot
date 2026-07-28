# Entry point: imports and delegates execution to the CLI handler when run as a script
import random
import time
from carlo_bot.bootstrap.cli import main

if __name__ == "__main__":
    # Ritardo casuale tra 0 e 15 minuti (900 secondi)
    # delay = random.randint(0, 900)
    print(f"PROCESS STARTED")
    # time.sleep(delay)

    # Avvia il workflow principale
    main()