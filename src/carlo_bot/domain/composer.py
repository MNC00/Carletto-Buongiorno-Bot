from html import escape


def build_subject() -> str:
    # Returns the fixed email subject line used for every message
    return "Il buongiorno che non ti meriti ma di cui hai bisogno!"


def _validate_quote(quote: str) -> None:
    # Guards against empty or whitespace-only quotes before they are embedded in email bodies
    if not quote or not quote.strip():
        raise ValueError("Quote cannot be empty.")


def build_plain_body(quote: str, saint: str, blasfemia: str) -> str:
    # Assembles the plain-text email body by combining quote, saint name, and blasfemia into a template
    _validate_quote(quote)

    return (
        "Buongiorno!\n\n"
        f'Tieni ben a mente che:\n"{quote}"\n\n'
        "Passa una buona giornata,\n"
        f"{saint.capitalize()} {blasfemia}\n\n"
        "Carlo"
    )


def build_html_body(quote: str, saint: str, blasfemia: str) -> str:
    # Assembles the HTML email body; HTML-escapes all dynamic content to prevent injection
    _validate_quote(quote)

    safe_quote = escape(quote.strip())
    safe_saint = escape(saint.strip().capitalize())
    safe_blasfemia = escape(blasfemia.strip())

    # References the inline photo via the Content-ID "carlo_photo" set by the email builder
    return f"""
    <html>
      <body>
        <p>Buongiorno!</p>
        <p>Tieni ben a mente che:<br><strong>\"{safe_quote}\"</strong></p>
        <p>
          <img src=\"cid:carlo_photo\" alt=\"Foto di Carlo\" style=\"max-width: 300px; height: auto;\">
        </p>
        <p>
          Passa una buona giornata,<br>
          <strong>{safe_saint.capitalize()} {safe_blasfemia}</strong>
        </p>
        <p>Carlo</p>
      </body>
    </html>
    """.strip()
