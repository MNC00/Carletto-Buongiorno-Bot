from pathlib import Path

from google import genai
from google.genai import types


def generate_message_body(
    quote: str,
    saint: str,
    api_key: str,
    system_prompt_file: Path,
) -> str:
    system_prompt = system_prompt_file.read_text(encoding="utf-8").strip()

    client = genai.Client(api_key=api_key)

    user_message = (
        f'Citazione del giorno: "{quote}"\n'
        f"Santo del giorno: {saint}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        ),
    )
    return response.text.strip()


def generate_birthday_message(
    name: str,
    api_key: str,
    system_prompt_file: Path,
) -> str:
    system_prompt = system_prompt_file.read_text(encoding="utf-8").strip()

    client = genai.Client(api_key=api_key)

    user_message = f"Il festeggiato di oggi è: {name}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        ),
    )
    return response.text.strip()
