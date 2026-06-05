# How To Run

Lancia i comandi dalla root del monorepo `UniversoCarletto/`.

Prerequisiti:
- virtualenv attivo, oppure uso esplicito di `.venv\Scripts\python.exe`
- `.env` configurato alla root
- `PYTHONPATH` impostato a `apps\buongiorno-bot\src`

## Bot giornaliero

Dry run, non invia:

```powershell
$env:PYTHONPATH="apps\buongiorno-bot\src"; .venv\Scripts\python.exe -m carlo_bot.main --dry-run
```

Invio reale:

```powershell
$env:PYTHONPATH="apps\buongiorno-bot\src"; .venv\Scripts\python.exe -m carlo_bot.main --send
```

## Invio comunicazioni generiche

Lo script generico e riutilizzabile e':

```text
apps\buongiorno-bot\scripts\send_announcement.py
```

Fa queste cose automaticamente:
- invia solo ai contatti `active=true`
- aggiunge il saluto personalizzato `Ciao {nickname},` con fallback sul nome
- allega inline `packages\branding\SuperCarlo.jpg` se presente
- se `SuperCarlo.jpg` manca, invia comunque la mail senza immagine

### Corpo della mail modificabile

Il corpo default della mail si modifica qui:

```text
apps\buongiorno-bot\data\announcements\birthdate_request.txt
```

Questo file contiene gia' il testo per chiedere:
- data di nascita
- se gli auguri devono essere pubblici a tutti o privati solo al destinatario

Lo script aggiunge da solo il saluto iniziale, quindi nel file non mettere `Ciao nome,`.

### Dry run con corpo default

Usa il file `birthdate_request.txt`:

```powershell
$env:PYTHONPATH="apps\buongiorno-bot\src"; .venv\Scripts\python.exe apps\buongiorno-bot\scripts\send_announcement.py --dry-run --subject "Carlo vuole ricordarsi il tuo compleanno"
```

### Invio reale con corpo default

```powershell
$env:PYTHONPATH="apps\buongiorno-bot\src"; .venv\Scripts\python.exe apps\buongiorno-bot\scripts\send_announcement.py --send --subject "Carlo vuole ricordarsi il tuo compleanno"
```

### Usare un altro file corpo

```powershell
$env:PYTHONPATH="apps\buongiorno-bot\src"; .venv\Scripts\python.exe apps\buongiorno-bot\scripts\send_announcement.py --dry-run --subject "Oggetto iniziativa" --body-file "percorso\al\testo.txt"
```

### Scrivere il corpo direttamente da comando

```powershell
$env:PYTHONPATH="apps\buongiorno-bot\src"; .venv\Scripts\python.exe apps\buongiorno-bot\scripts\send_announcement.py --dry-run --subject "Oggetto iniziativa" --body "Testo della comunicazione"
```

Per inviare davvero, sostituisci `--dry-run` con `--send`.