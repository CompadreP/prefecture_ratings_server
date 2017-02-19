from datetime import datetime
from typing import Tuple

from cryptography.fernet import Fernet

from django.conf import settings


def decrypt_token(token: str) -> Tuple[str, datetime]:
    encoded_token = token.encode('utf-8')
    f = Fernet(settings.SECRET_FERNET_KEY)
    email, str_datetime = str(f.decrypt(encoded_token), 'utf-8').split(' | ')
    parsed_datetime = datetime.strptime(str_datetime, "%Y-%m-%d %H:%M:%S.%f")
    return email, parsed_datetime
