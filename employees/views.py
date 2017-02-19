from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import FormView
from django.views.generic import TemplateView

from employees.common import decrypt_token
from employees.forms import PasswordSetForm


def is_token_expired(parsed_datetime: datetime):
    if datetime.now() - parsed_datetime > timedelta(seconds=settings.PASSWORD_SET_FORM_TTL_SECONDS):
        return True
    else:
        return False


class PasswordSetView(FormView):
    template_name = "password_set_form.html"
    form_class = PasswordSetForm
    success_url = '/password_set/success'

    def get(self, request, *args, **kwargs):
        url_token = request.path[request.path.rfind('/') + 1:]
        _, parsed_datetime = decrypt_token(url_token)
        if is_token_expired(parsed_datetime):
            return HttpResponse("<html><body>Время действия ссылки "
                                "истекло, обратитесь к администратору для "
                                "получения новой.</body></html>")
        else:
            return super(PasswordSetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.url_token = request.path[request.path.rfind('/') + 1:]
        email, parsed_datetime = decrypt_token(self.url_token)

        if is_token_expired(parsed_datetime):
            return HttpResponse("<html><body>Время действия ссылки "
                                "истекло, обратитесь к администратору для "
                                "получения новой.</body></html>")
        else:
            return super(PasswordSetView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.set_user_password(self.url_token)
        return super(PasswordSetView, self).form_valid(form)


class PasswordSetSuccess(TemplateView):
    template_name = "password_set_success.html"

