# Carletto Buongiorno Bot - Context Hub

## Mission

Send a daily good-morning email with a randomly selected quote, saint, blasfemia, and Carlo photo to all active contacts.

## Scope

- Load contacts from JSON.
- Load quotes, saints, and blasfemie from text files.
- Load photos from a local directory.
- Select random content.
- Compose plain-text and HTML email bodies.
- Build and send an email through SMTP SSL.
- Support dry-run execution.

## Business Invariants

- Email subject must remain: `Il buongiorno che non ti meriti ma di cui hai bisogno!`
- Inline image content ID must remain: `carlo_photo`
- Allowed image suffixes are `.jpg`, `.jpeg`, `.png`
- Contacts data must contain `name`, `email`, and `active`
- Quote, saint, and blasfemia sources are newline-delimited text files with blank lines ignored
- Random selection continues to rely on Python `random.choice`

## Data Contracts

### Contacts

- File: `data/contacts/contacts.json`
- Type: JSON list of objects
- Required fields per item:
  - `name: str`
  - `email: str`
  - `active: bool`

### Quotes

- File: `data/quotes/quotes.txt`
- Non-empty lines become quote entries

### Saints

- File: `data/quotes/saints.txt`
- Non-empty lines become saint entries

### Blasfemie

- File: `data/quotes/blasfemie.txt`
- Non-empty lines become blasfemia entries

### Photos

- Directory: `data/photos`
- Files are accepted only if suffix is `.jpg`, `.jpeg`, or `.png`

## Configuration Catalog

| Variable | Required | Default | Meaning |
| --- | --- | --- | --- |
| `APP_ENV` | no | `development` | Runtime environment label |
| `SMTP_HOST` | yes | none | SMTP host |
| `SMTP_PORT` | yes | none | SMTP port, cast to integer |
| `SMTP_USERNAME` | yes | none | SMTP username |
| `SMTP_PASSWORD` | yes | none | SMTP password or app password |
| `SMTP_SENDER` | yes | none | From address |
| `CONTACTS_FILE` | no | `data/contacts/contacts.json` | Contacts file path |
| `QUOTES_FILE` | no | `data/quotes/quotes.txt` | Quotes file path |
| `SAINTS_FILE` | no | `data/quotes/saints.txt` | Saints file path |
| `BLASFEMIE_FILE` | no | `data/quotes/blasfemie.txt` | Blasfemie file path |
| `PHOTOS_DIR` | no | `data/photos` | Photos directory path |
| `DRY_RUN` | no | `true` | Enables no-send execution |

Secrets stay in `.env` and are not duplicated here.

## Runtime Topology

1. `carlo_bot.main` delegates to bootstrap CLI.
2. Bootstrap loads config and resolves CLI overrides.
3. Application workflow resolves project paths.
4. Domain loaders read and validate local inputs.
5. Domain picker selects random content.
6. Domain composer builds subject and bodies.
7. Infrastructure email builder creates the message.
8. Infrastructure sender dispatches only when dry-run is disabled.

## Module Map

- `src/carlo_bot/bootstrap`: CLI parsing and runtime helpers
- `src/carlo_bot/application`: orchestration workflow
- `src/carlo_bot/domain`: business capabilities
- `src/carlo_bot/infrastructure`: configuration and SMTP adapters
- `src/carlo_bot/agents`: lightweight multi-agent scaffold
- `scripts`: operational utilities not required by the runtime package

## Agent Scaffold

The repository is prepared for future agent orchestration through atomic tasks:

- `load_inputs`
- `select_content`
- `compose_message`
- `build_email`
- `send_email`

This phase adds only structure and contracts. No LLM, queue, or persistent agent state is introduced.

## Test Baseline

- Loader and picker tests define core data and selection contracts.
- Composer and email sender tests were originally out of sync with the implementation.
- Compatibility exports are acceptable during the transition as long as runtime behavior stays unchanged.
