from google.genai.errors import ClientError as GeminiClientError, ServerError as GeminiServerError

from carlo_bot.domain.composer import (
    build_birthday_fallback_private,
    build_birthday_fallback_public,
    build_html_body,
    build_html_body_ai,
    build_plain_body,
    build_plain_body_ai,
    build_subject,
)

_LLM_OVERLOAD_INCIPIT = "Eh scusa, non oggi: a Google nun glie andava di collaborà."
_LLM_BILLING_INCIPIT = "Eh mi devi scusare, ma Google mo vuole i sordi e ancora non gliel'abbiamo dati: oggi niente AI per te."
_LLM_GENERIC_INCIPIT = "Eh oggi Google stava in giornata no: niente AI, tocca annà de backup."
_LLM_REASON_OVERLOAD = "overload"
_LLM_REASON_BILLING = "billing"
_LLM_REASON_GENERIC = "generic"


def _classify_llm_error(exc: Exception) -> str:
    """Returns normalized reason for an LLM failure."""
    if isinstance(exc, GeminiServerError):
        return _LLM_REASON_OVERLOAD
    if isinstance(exc, GeminiClientError):
        msg = str(exc).lower()
        if any(k in msg for k in ("billing", "quota", "credit", "payment")):
            return _LLM_REASON_BILLING
        return _LLM_REASON_OVERLOAD
    return _LLM_REASON_GENERIC


def _reason_to_text(reason: str) -> str:
    if reason == _LLM_REASON_BILLING:
        return "problema de credito"
    if reason == _LLM_REASON_OVERLOAD:
        return "sovraccarico lato Google"
    return "intoppo tecnico"


def _single_reason_incipit(reason: str) -> str:
    if reason == _LLM_REASON_BILLING:
        return _LLM_BILLING_INCIPIT
    if reason == _LLM_REASON_OVERLOAD:
        return _LLM_OVERLOAD_INCIPIT
    return _LLM_GENERIC_INCIPIT


def _build_combined_fallback_incipit(
    body_attempted: bool,
    body_ok: bool,
    body_reason: str | None,
    closing_attempted: bool,
    closing_ok: bool,
    closing_reason: str | None,
) -> str | None:
    if body_attempted and closing_attempted:
        if body_ok and closing_ok:
            return None
        if body_ok and not closing_ok:
            return (
                "Google oggi ha collaborato a meta: il corpo me l'ha fatto, "
                f"ma sul closing ha mollato ({_reason_to_text(closing_reason or _LLM_REASON_GENERIC)})."
            )
        if not body_ok and closing_ok:
            return (
                "Google oggi ha collaborato a meta: il closing me l'ha fatto, "
                f"ma il corpo no ({_reason_to_text(body_reason or _LLM_REASON_GENERIC)})."
            )

        if body_reason == closing_reason:
            return _single_reason_incipit(body_reason or _LLM_REASON_GENERIC)

        return (
            "Google oggi m'ha fatto il doppio pacco: "
            f"corpo saltato ({_reason_to_text(body_reason or _LLM_REASON_GENERIC)}) "
            f"e pure closing saltato ({_reason_to_text(closing_reason or _LLM_REASON_GENERIC)})."
        )

    if body_attempted:
        if body_ok:
            return None
        return _single_reason_incipit(body_reason or _LLM_REASON_GENERIC)

    if closing_attempted:
        if closing_ok:
            return None
        return _single_reason_incipit(closing_reason or _LLM_REASON_GENERIC)

    return None


from carlo_bot.bootstrap.runtime import get_project_root
from carlo_bot.infrastructure.llm import (
    generate_birthday_message,
    generate_message_body,
    rewrite_email_closing,
)
from carlo_bot.domain.picker import (
    pick_active_contacts,
    pick_birthday_contacts,
    pick_random_blasfemia,
    pick_random_photo,
    pick_random_quote,
    pick_random_saint,
)
from carlo_bot.infrastructure.config import AppConfig
from carlo_bot.infrastructure.email.builder import build_email_message
from carlo_bot.infrastructure.email.sender import send_email
from carlo_bot.infrastructure.storage import build_storage_provider
from carlo_bot.infrastructure.unsubscribe import build_unsubscribe_url


def run_workflow(config: AppConfig, dry_run: bool) -> None:
    # Instantiates the storage provider (filesystem or Google Workspace) based on STORAGE_BACKEND
    project_root = get_project_root()
    storage_provider = build_storage_provider(config=config, project_root=project_root)

    # Loads all datasets from the configured backend in one pass
    contacts = storage_provider.load_contacts()
    quotes = storage_provider.load_quotes()
    photo_assets = storage_provider.load_photo_assets()
    saints = storage_provider.load_saints()
    blasfemie = storage_provider.load_blasfemie()

    # Filters contacts to active-only and picks one random item from each content dataset
    active_contacts = pick_active_contacts(contacts)
    selected_quote = pick_random_quote(quotes)
    selected_photo = pick_random_photo(photo_assets)
    selected_saint = pick_random_saint(saints)
    selected_blasfemia = pick_random_blasfemia(blasfemie)

    # Builds the shared email subject from the selected content
    subject = build_subject()
    recipients = [contact["email"] for contact in active_contacts]

    # Prints a structured summary of configuration, loaded data, selections, and email details
    print("=== Configuration ===")
    print(f"Environment: {config.app_env}")
    print(f"Dry run: {dry_run}")

    print("\n=== Loading summary ===")
    print(f"Contacts loaded: {len(contacts)}")
    print(f"Active contacts: {len(active_contacts)}")
    print(f"Quotes loaded: {len(quotes)}")
    print(f"Photos loaded: {len(photo_assets)}")

    print("\n=== Selection result ===")
    print(f"Selected quote: {selected_quote}")
    print(f"Selected saint: {selected_saint}")
    print(f"Selected blasfemia: {selected_blasfemia}")
    print(f"Selected photo: {selected_photo.name}")

    print("\n=== Composed email ===")
    print(f"Subject: {subject}")
    print(f"Recipients: {recipients}")
    print(f"Inline image: {selected_photo.name}")

    print("\n=== Delivery ===")

    # Attempts to generate the message body via LLM; falls back to the static template on any failure
    ai_generated_body: str | None = None
    body_attempted = bool(config.gemini_api_key)
    body_ok = False
    body_error_reason: str | None = None
    if body_attempted:
        try:
            prompt_path = get_project_root() / config.llm_prompt_file
            ai_generated_body = generate_message_body(
                quote=selected_quote,
                saint=selected_saint,
                api_key=config.gemini_api_key,
                system_prompt_file=prompt_path,
            )
            body_ok = True
            print(f"LLM body generated ({len(ai_generated_body)} chars)")
        except (GeminiServerError, GeminiClientError) as exc:
            body_error_reason = _classify_llm_error(exc)
            print(f"LLM generation failed, using static template: {exc}")
        except Exception as exc:  # noqa: BLE001
            body_error_reason = _classify_llm_error(exc)
            print(f"LLM generation failed, using static template: {exc}")
    else:
        print("GEMINI_API_KEY not set, using static template")

    # Optionally rewrites the final closing with LLM, with fallback to the original closing on failure
    rewritten_closing: str | None = None
    closing_rewrite_enabled = getattr(config, "closing_rewrite_enabled", True)
    closing_rewrite_prompt_file = getattr(
        config,
        "closing_rewrite_prompt_file",
        "apps/buongiorno-bot/data/prompts/closing_rewrite_prompt.txt",
    )
    closing_attempted = bool(config.gemini_api_key and closing_rewrite_enabled)
    closing_ok = False
    closing_error_reason: str | None = None
    if closing_attempted:
        try:
            rewrite_prompt_path = get_project_root() / closing_rewrite_prompt_file
            rewritten_closing_candidate = rewrite_email_closing(
                saint=selected_saint,
                blasfemia=selected_blasfemia,
                api_key=config.gemini_api_key,
                system_prompt_file=rewrite_prompt_path,
            )
            if rewritten_closing_candidate.strip():
                rewritten_closing = rewritten_closing_candidate.strip()
                closing_ok = True
                print(f"LLM closing rewritten ({len(rewritten_closing)} chars)")
            else:
                closing_error_reason = _LLM_REASON_GENERIC
                print("LLM closing rewrite returned empty output, using default closing")
        except (GeminiServerError, GeminiClientError) as exc:
            closing_error_reason = _classify_llm_error(exc)
            print(f"LLM closing rewrite failed, using default closing: {exc}")
        except Exception as exc:  # noqa: BLE001
            closing_error_reason = _classify_llm_error(exc)
            print(f"LLM closing rewrite failed, using default closing: {exc}")

    fallback_incipit = _build_combined_fallback_incipit(
        body_attempted=body_attempted,
        body_ok=body_ok,
        body_reason=body_error_reason,
        closing_attempted=closing_attempted,
        closing_ok=closing_ok,
        closing_reason=closing_error_reason,
    )

    # Detects birthday contacts among active contacts
    birthday_contacts = pick_birthday_contacts(active_contacts)
    birthday_emails = {c["email"] for c in birthday_contacts}
    public_birthday_contacts = [c for c in birthday_contacts if c.get("birthday_public", True)]

    if birthday_contacts:
        print(f"Birthday contacts today: {[c.get('name') for c in birthday_contacts]}")

    # Generates AI birthday messages per birthday contact; falls back to static on failure
    birthday_ai_messages: dict[str, str] = {}
    if birthday_contacts and config.gemini_api_key:
        birthday_prompt_path = get_project_root() / config.birthday_prompt_file
        for bday_contact in birthday_contacts:
            bday_name = bday_contact.get("name", "")
            try:
                birthday_ai_messages[bday_contact["email"]] = generate_birthday_message(
                    name=bday_name,
                    api_key=config.gemini_api_key,
                    system_prompt_file=birthday_prompt_path,
                )
                print(f"Birthday AI message generated for {bday_name}")
            except Exception as exc:  # noqa: BLE001
                print(f"Birthday AI generation failed for {bday_name}, using fallback: {exc}")

    # Builds one message per recipient so later steps can customize content safely per contact
    preview_body: str | None = None
    preview_recipient: str | None = None
    for contact in active_contacts:
        recipient = contact["email"]
        recipient_name = contact.get("name")
        nickname = contact.get("nickname")
        unsubscribe_url = _build_recipient_unsubscribe_url(config, recipient)

        # Determine birthday section for this contact
        birthday_section = _build_contact_birthday_section(
            contact=contact,
            birthday_emails=birthday_emails,
            birthday_contacts=birthday_contacts,
            public_birthday_contacts=public_birthday_contacts,
            birthday_ai_messages=birthday_ai_messages,
        )

        if ai_generated_body:
            plain_body = build_plain_body_ai(
                ai_generated_body,
                selected_saint,
                selected_blasfemia,
                recipient_name=recipient_name,
                unsubscribe_url=unsubscribe_url,
                nickname=nickname,
                birthday_section=birthday_section,
                closing_override=rewritten_closing,
                fallback_incipit=fallback_incipit,
            )
            html_body = build_html_body_ai(
                ai_generated_body,
                selected_saint,
                selected_blasfemia,
                recipient_name=recipient_name,
                unsubscribe_url=unsubscribe_url,
                nickname=nickname,
                birthday_section=birthday_section,
                closing_override=rewritten_closing,
                fallback_incipit=fallback_incipit,
            )
        else:
            plain_body = build_plain_body(
                selected_quote,
                selected_saint,
                selected_blasfemia,
                recipient_name=recipient_name,
                unsubscribe_url=unsubscribe_url,
                nickname=nickname,
                birthday_section=birthday_section,
                closing_override=rewritten_closing,
                fallback_incipit=fallback_incipit,
            )
            html_body = build_html_body(
                selected_quote,
                selected_saint,
                selected_blasfemia,
                recipient_name=recipient_name,
                unsubscribe_url=unsubscribe_url,
                nickname=nickname,
                birthday_section=birthday_section,
                closing_override=rewritten_closing,
                fallback_incipit=fallback_incipit,
            )
        message = build_email_message(
            sender=config.smtp_sender,
            recipients=[recipient],
            subject=subject,
            plain_body=plain_body,
            html_body=html_body,
            image_asset=selected_photo,
        )

        if dry_run:
            print(f"Prepared email for: {recipient}")
            if preview_body is None:
                preview_body = plain_body
                preview_recipient = recipient
            continue

        send_email(config, message)
        print(f"Email sent to: {recipient}")

    if dry_run:
        if preview_body is not None:
            print(f"\n=== Plain text body preview (to {preview_recipient}) ===")
            print(preview_body)
            print("=== End plain text body preview ===")
        print("\nDRY_RUN enabled: emails not sent.")
        return

    print("\nEmail sent successfully.")


def _build_recipient_unsubscribe_url(config: AppConfig, recipient: str) -> str | None:
    if config.unsubscribe_base_url is None or config.unsubscribe_secret is None:
        return None

    return build_unsubscribe_url(config.unsubscribe_base_url, recipient, config.unsubscribe_secret)


def _build_contact_birthday_section(
    *,
    contact: dict,
    birthday_emails: set[str],
    birthday_contacts: list[dict],
    public_birthday_contacts: list[dict],
    birthday_ai_messages: dict[str, str],
) -> str | None:
    if not birthday_contacts:
        return None

    recipient = contact["email"]
    parts: list[str] = []

    # If this contact is the birthday person, add private birthday greeting
    if recipient in birthday_emails:
        name = contact.get("name", "")
        ai_msg = birthday_ai_messages.get(recipient)
        parts.append(ai_msg if ai_msg else build_birthday_fallback_private(name))

    # Add public birthday greetings for other birthday contacts (only those with birthday_public=True)
    for bday_contact in public_birthday_contacts:
        if bday_contact["email"] == recipient:
            continue
        full_name = f"{bday_contact.get('name', '')} {bday_contact.get('cognome', '')}".strip()
        ai_msg = birthday_ai_messages.get(bday_contact["email"])
        if ai_msg:
            parts.append(f"Oggi festeggiamo {full_name}!\n{ai_msg}")
        else:
            parts.append(build_birthday_fallback_public(full_name))

    if not parts:
        return None

    return "\n\n".join(parts)
