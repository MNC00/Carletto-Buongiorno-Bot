import pytest

from carlo_bot.domain.composer import (
    build_birthday_fallback_private,
    build_birthday_fallback_public,
    build_html_body,
    build_plain_body,
    build_subject,
)


def test_build_subject_returns_expected_subject():
    result = build_subject()

    assert result == "Il buongiorno che non ti meriti ma di cui hai bisogno!"


def test_build_body_includes_quote():
    quote = "Oggi spacchi tutto."

    result = build_plain_body(quote, "San Gennaro", "culone")

    assert "Buongiorno!" in result
    assert "Tieni ben a mente che" in result
    assert quote in result


def test_build_body_raises_if_quote_is_empty():
    with pytest.raises(ValueError, match="Quote cannot be empty"):
        build_plain_body("", "San Gennaro", "culone")


def test_build_body_raises_if_quote_is_only_spaces():
    with pytest.raises(ValueError, match="Quote cannot be empty"):
        build_plain_body("   ", "San Gennaro", "culone")


def test_build_plain_body_includes_unsubscribe_footer_when_url_is_provided():
    unsubscribe_url = "https://example.com/unsubscribe?email=alice@example.com&sig=abc"

    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", unsubscribe_url=unsubscribe_url)

    assert "Per non ricevere piu questa mail" in result
    assert unsubscribe_url in result


def test_build_html_body_includes_unsubscribe_link_when_url_is_provided():
    unsubscribe_url = "https://example.com/unsubscribe?email=alice@example.com&sig=abc"

    result = build_html_body("Oggi spacchi tutto.", "San Gennaro", "culone", unsubscribe_url=unsubscribe_url)

    assert "clicca qui" in result
    assert "href=\"https://example.com/unsubscribe?email=alice@example.com&amp;sig=abc\"" in result


def test_build_plain_body_includes_recipient_name_when_provided():
    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="Alice")

    assert result.startswith("Buongiorno Alice!")


def test_build_html_body_includes_recipient_name_when_provided():
    result = build_html_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="Alice")

    assert "<p>Buongiorno Alice!</p>" in result


def test_build_plain_body_falls_back_to_generic_greeting_for_blank_name():
    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="   ")

    assert result.startswith("Buongiorno!")


# --- Nickname tests ---


def test_build_plain_body_uses_nickname_when_provided():
    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="Alice", nickname="Alicetta")

    assert result.startswith("Buongiorno Alicetta!")


def test_build_html_body_uses_nickname_when_provided():
    result = build_html_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="Alice", nickname="Alicetta")

    assert "<p>Buongiorno Alicetta!</p>" in result


def test_build_plain_body_falls_back_to_name_when_nickname_is_none():
    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="Alice", nickname=None)

    assert result.startswith("Buongiorno Alice!")


def test_build_plain_body_falls_back_to_name_when_nickname_is_empty():
    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="Alice", nickname="")

    assert result.startswith("Buongiorno Alice!")


def test_build_plain_body_generic_greeting_when_both_nickname_and_name_empty():
    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="", nickname="")

    assert result.startswith("Buongiorno!")


# --- Birthday section tests ---


def test_build_plain_body_includes_birthday_section_when_provided():
    result = build_plain_body(
        "Oggi spacchi tutto.", "San Gennaro", "culone",
        recipient_name="Alice",
        birthday_section="Auguri vecchia!",
    )

    assert "Buongiorno Alice!" in result
    assert "Auguri vecchia!" in result
    assert "\U0001F382" not in result
    assert result.index("Auguri vecchia!") < result.index("Tieni ben a mente che")


def test_build_html_body_includes_birthday_section_when_provided():
    result = build_html_body(
        "Oggi spacchi tutto.", "San Gennaro", "culone",
        recipient_name="Alice",
        birthday_section="Auguri vecchia!",
    )

    assert "\U0001F382 Auguri vecchia!" in result


def test_build_plain_body_no_birthday_section_when_none():
    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="Alice")

    assert "\U0001F382" not in result


def test_build_html_body_escapes_birthday_section():
    result = build_html_body(
        "Oggi spacchi tutto.", "San Gennaro", "culone",
        recipient_name="Alice",
        birthday_section="Auguri <script>alert('xss')</script>",
    )

    assert "<script>" not in result
    assert "&lt;script&gt;" in result


def test_build_birthday_fallback_private():
    result = build_birthday_fallback_private("Mario")

    assert "Mario" in result


def test_build_birthday_fallback_public():
    result = build_birthday_fallback_public("Mario Rossi")

    assert "Mario Rossi" in result
