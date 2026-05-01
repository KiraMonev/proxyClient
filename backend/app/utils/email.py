import logging

from app.config import settings

logger = logging.getLogger(__name__)


def send_email_console(to_email: str, subject: str, body: str) -> None:
    """Console email backend — prints email to logs."""
    logger.info("EMAIL (console backend)")
    logger.info(f"To: {to_email}")
    logger.info(f"From: {settings.EMAIL_FROM}")
    logger.info(f"Subject: {subject}")
    logger.info("-" * 40)
    logger.info(body)


def send_email_smtp(to_email: str, subject: str, body: str) -> None:
    """Send email via SMTP (Mailtrap or other provider)."""
    import smtplib
    from email.mime.text import MIMEText

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, [to_email], msg.as_string())


def send_email(to_email: str, subject: str, body: str) -> None:
    """Send email using the configured backend."""
    if settings.EMAIL_BACKEND == "console":
        send_email_console(to_email, subject, body)
    else:
        send_email_smtp(to_email, subject, body)
