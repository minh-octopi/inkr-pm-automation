"""Delivers the PM layer's report. Mock now; real sending needs SMTP
credentials (config.EMAIL_SENDER / EMAIL_APP_PASSWORD), not present yet.
"""
from abc import ABC, abstractmethod


class EmailClient(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None:
        ...


class MockEmailClient(EmailClient):
    """In-memory stand-in so the send step can be exercised without real
    credentials or actually emailing anyone."""

    def __init__(self):
        self.sent: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append({"to": to, "subject": subject, "body": body})


class SMTPEmailClient(EmailClient):
    """Real client via Gmail SMTP.

    UNVERIFIED — needs EMAIL_SENDER and EMAIL_APP_PASSWORD (a Gmail app
    password generated for this account, not your normal login password).
    """

    def __init__(self, sender: str, app_password: str):
        self._sender = sender
        self._app_password = app_password

    def send(self, to: str, subject: str, body: str) -> None:
        import smtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"] = self._sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self._sender, self._app_password)
            server.send_message(msg)
