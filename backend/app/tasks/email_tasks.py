from app.tasks.celery_app import celery_app
from app.utils.email import send_email


@celery_app.task(name="send_activation_email")
def send_activation_email(to_email: str, activation_key: str) -> dict:
    """Send an email with the activation key to the user."""
    subject = "Ваш ключ активации — Proxy Service"
    body = f"{activation_key}"
    send_email(to_email, subject, body)
    return {"status": "sent", "to": to_email}
