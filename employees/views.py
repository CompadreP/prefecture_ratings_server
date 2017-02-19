# view for handling password setup for users
# generating random hash on base of user's email
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

from django.conf import settings
from django.http import HttpResponse


def email_verification(request):
    url_token = request.path[request.path.rfind('/') + 1:]
    token = url_token.encode('utf-8')
    f = Fernet(settings.SECRET_FERNET_KEY)
    email, str_datetime = str(f.decrypt(token), 'utf-8').split(' | ')
    parsed_datetime = datetime.strptime(str_datetime, "%Y-%m-%d %H:%M:%S.%f")
    max_timedelta = timedelta(days=1)
    if datetime.now() - parsed_datetime > max_timedelta:
        return HttpResponse("<html><body>Время действия ссылки "
                            "истекло, обратитесь к администратору для "
                            "получения новой.</body></html>")

    else:
        return HttpResponse("<html><body>А тут формочка для установки пароля</body></html>")


