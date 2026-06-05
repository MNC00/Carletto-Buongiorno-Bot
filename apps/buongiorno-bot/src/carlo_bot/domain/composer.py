from html import escape


def build_subject() -> str:
    # Returns the fixed email subject line used for every message
    return "Il buongiorno che non ti meriti ma di cui hai bisogno!"


def _validate_quote(quote: str) -> None:
    # Guards against empty or whitespace-only quotes before they are embedded in email bodies
    if not quote or not quote.strip():
        raise ValueError("Quote cannot be empty.")


def _build_greeting(recipient_name: str | None, nickname: str | None = None) -> str:
    display_name = nickname or (recipient_name.strip() if recipient_name else None)

    if not display_name or not display_name.strip():
        return "Buongiorno!"

    return f"Buongiorno {display_name.strip()}!"


def build_birthday_fallback_private(name: str) -> str:
    return f"Oggi è il tuo giorno, {name}! Tanti auguri, anche se non te li meriti!"


def build_birthday_fallback_public(full_name: str) -> str:
    return f"Oggi festeggiamo {full_name}! Tanti auguri!"


def _build_birthday_section(birthday_text: str) -> str:
    if not birthday_text:
        return ""
    return f"\U0001F382 {birthday_text.strip()}\n\n"


def _build_html_birthday_section(birthday_text: str) -> str:
    if not birthday_text:
        return ""
    safe_text = escape(birthday_text.strip()).replace("\n", "<br>")
    return f'        <p>\U0001F382 {safe_text}</p>\n'


def _build_plain_unsubscribe_footer(unsubscribe_url: str | None) -> str:
    if unsubscribe_url is None:
        return ""

    return (
        "\n\n"
        "Per non ricevere piu questa mail, usa questo link:\n"
        f"{unsubscribe_url}"
    )


def _build_html_unsubscribe_footer(unsubscribe_url: str | None) -> str:
    if unsubscribe_url is None:
        return ""

    safe_url = escape(unsubscribe_url.strip(), quote=True)
    return (
        "\n        <hr>\n"
        "        <p style=\"font-size: 0.9em;\">"
        "Se vuoi disiscriverti, "
        f"<a href=\"{safe_url}\">clicca qui</a>."
        "</p>"
    )


def build_plain_body(
    quote: str,
    saint: str,
    blasfemia: str,
    recipient_name: str | None = None,
    unsubscribe_url: str | None = None,
    nickname: str | None = None,
    birthday_section: str | None = None,
) -> str:
    # Assembles the plain-text email body by combining quote, saint name, and blasfemia into a template
    _validate_quote(quote)
    greeting = _build_greeting(recipient_name, nickname=nickname)
    bday = _build_birthday_section(birthday_section) if birthday_section else ""

    return (
        f"{greeting}\n\n"
        f"{bday}"
        f'Tieni ben a mente che:\n"{quote}"\n\n'
        "Passa una buona giornata,\n"
        f"{saint.capitalize()} {blasfemia}\n\n"
        "Carlo"
        f"{_build_plain_unsubscribe_footer(unsubscribe_url)}"
    )


def build_plain_body_ai(
    generated_body: str,
    saint: str,
    blasfemia: str,
    recipient_name: str | None = None,
    unsubscribe_url: str | None = None,
    nickname: str | None = None,
    birthday_section: str | None = None,
) -> str:
    # Assembles the plain-text email body using an AI-generated body instead of the static template
    if not generated_body or not generated_body.strip():
        raise ValueError("generated_body cannot be empty.")
    greeting = _build_greeting(recipient_name, nickname=nickname)
    bday = _build_birthday_section(birthday_section) if birthday_section else ""

    return (
        f"{greeting}\n\n"
        f"{bday}"
        f"{generated_body.strip()}\n\n"
        "Passa una buona giornata,\n"
        f"{saint.capitalize()} {blasfemia}\n\n"
        "Carlo"
        f"{_build_plain_unsubscribe_footer(unsubscribe_url)}"
    )


def build_html_body(
    quote: str,
    saint: str,
    blasfemia: str,
    recipient_name: str | None = None,
    unsubscribe_url: str | None = None,
    nickname: str | None = None,
    birthday_section: str | None = None,
) -> str:
    # Assembles the HTML email body; HTML-escapes all dynamic content to prevent injection
    _validate_quote(quote)

    greeting = escape(_build_greeting(recipient_name, nickname=nickname))
    safe_quote = escape(quote.strip())
    safe_saint = escape(saint.strip().capitalize())
    safe_blasfemia = escape(blasfemia.strip())
    bday_html = _build_html_birthday_section(birthday_section) if birthday_section else ""

    # References the inline photo via the Content-ID "carlo_photo" set by the email builder
    return f"""
    <html>
      <body>
        <p>{greeting}</p>
{bday_html}        <p>Tieni ben a mente che:<br><strong>\"{safe_quote}\"</strong></p>
        <p>
          <img src=\"cid:carlo_photo\" alt=\"Foto di Carlo\" style=\"max-width: 300px; height: auto;\">
        </p>
        <p>
          Passa una buona giornata,<br>
          <strong>{safe_saint.capitalize()} {safe_blasfemia}</strong>
        </p>
        <p>Carlo</p>
        {_build_html_unsubscribe_footer(unsubscribe_url)}
      </body>
    </html>
    """.strip()


def build_html_body_ai(
    generated_body: str,
    saint: str,
    blasfemia: str,
    recipient_name: str | None = None,
    unsubscribe_url: str | None = None,
    nickname: str | None = None,
    birthday_section: str | None = None,
) -> str:
    # Assembles the HTML email body using an AI-generated body; HTML-escapes all dynamic content
    if not generated_body or not generated_body.strip():
        raise ValueError("generated_body cannot be empty.")

    greeting = escape(_build_greeting(recipient_name, nickname=nickname))
    safe_body = escape(generated_body.strip())
    safe_saint = escape(saint.strip().capitalize())
    safe_blasfemia = escape(blasfemia.strip())
    bday_html = _build_html_birthday_section(birthday_section) if birthday_section else ""

    # Converts newlines in the AI body to <br> so paragraph breaks survive in HTML
    safe_body_html = safe_body.replace("\n", "<br>")

    return f"""
    <html>
      <body>
        <p>{greeting}</p>
{bday_html}        <p>{safe_body_html}</p>
        <p>
          <img src="cid:carlo_photo" alt="Foto di Carlo" style="max-width: 300px; height: auto;">
        </p>
        <p>
          Passa una buona giornata,<br>
          <strong>{safe_saint.capitalize()} {safe_blasfemia}</strong>
        </p>
        <p>Carlo</p>
        {_build_html_unsubscribe_footer(unsubscribe_url)}
      </body>
    </html>
    """.strip()
