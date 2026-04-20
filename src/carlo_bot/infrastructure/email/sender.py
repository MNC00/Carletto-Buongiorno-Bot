import smtplib
import ssl
from email.message import EmailMessage

from carlo_bot.infrastructure.config import AppConfig


def send_email(config: AppConfig, message: EmailMessage) -> None:
    # Opens a TLS-encrypted SMTP_SSL connection, authenticates with stored credentials, and sends the message
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port, context=context) as server:
        server.login(config.smtp_username, config.smtp_password)
        server.send_message(message)
