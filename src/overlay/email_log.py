import os
import platform
import smtplib
import ssl
import traceback
from types import TracebackType
from typing import Type

from overlay.settings import settings

port = 465  # Required for SMTP_SLL
password = ""
sender_email = "maguro.overlay.debug@gmail.com"
receiver_email = sender_email
context = ssl.create_default_context()


def send_email_log(version: str, exc_type: Type[BaseException],
                   exc_value: Exception, exc_tback: TracebackType):
    """Sends log to overlay email"""

    # Password is set only in the compiled version
    if not password:
        return

    # Prepare the subject and the email message
    rel_path = os.path.relpath(exc_tback.tb_frame.f_code.co_filename)

    subject = (f"{version} | "
               f"{rel_path} {exc_tback.tb_lineno} | "
               f"{exc_type.__name__}: {exc_value}")

    formatted = ''.join(
        traceback.format_exception(exc_type, exc_value, exc_tback))

    message = (f"player_name: {settings.player_name}\n"
               f"steam_id: {settings.steam_id}\n"
               f"profile_id: {settings.profile_id}\n"
               f"version: {version}\n"
               f"platform: {platform.platform()}\n\n"
               f"{formatted}\n\n"
               f"locals: {exc_tback.tb_frame.f_locals}")

    # Send
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email,
                        f"Subject: {subject}\n\n{message}")
