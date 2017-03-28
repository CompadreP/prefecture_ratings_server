import datetime
from urllib import parse

from cryptography.fernet import Fernet

from django.conf import settings
from django.core import mail

from apps.common.celery_app import app


def generate_url_token(email: str):
    f = Fernet(settings.SECRET_FERNET_KEY)
    token = f.encrypt((email + ' | '
                       + str(datetime.datetime.now())).encode('utf-8'))
    return parse.quote(token.decode('utf-8'))


@app.task
def generate_token_and_send_email(email: str, subject: str, body: str):
    url_token = generate_url_token(email)
    with mail.get_connection() as connection:
        mail.EmailMessage(
            subject=subject,
            body=body.format(base_url=settings.BASE_URL, url_token=url_token),
            to=[email],
            connection=connection,
        ).send()
