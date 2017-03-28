from django.core import mail
from typing import List

from apps.common.celery_app import app


@app.task
def send_emails(emails: List[str], subject: str, body: str):
    with mail.get_connection() as connection:
        mail.EmailMessage(
            subject=subject,
            body=body,
            to=emails,
            connection=connection,
        ).send()
