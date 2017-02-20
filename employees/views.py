from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.request import Request

from rest_framework.views import APIView
from rest_framework.response import Response

from employees.common import decrypt_token
from employees.forms import PasswordSetForm
from employees.models import RegionEmployee, PrefectureEmployee
from employees.serializers import RatingsUserSerializer, \
    PrefectureEmployeeSerializer, RegionEmployeeSerializer


###############################################################################
# Password set views (standard django)
###############################################################################


def is_verification_token_expired(parsed_datetime: datetime):
    if datetime.now() - parsed_datetime > timedelta(seconds=settings.PASSWORD_SET_FORM_TTL_SECONDS):
        return True
    else:
        return False


expired_response = HttpResponse("<html><body>Время действия ссылки "
                                "истекло, обратитесь к администратору для "
                                "получения новой.</body></html>")


class PasswordSetView(FormView):
    template_name = "password_set_form.html"
    form_class = PasswordSetForm
    success_url = '/password_set/success'

    def get(self, request, *args, **kwargs):
        url_token = request.path[request.path.rfind('/') + 1:]
        _, parsed_datetime = decrypt_token(url_token)
        if is_verification_token_expired(parsed_datetime):
            return expired_response
        else:
            return super(PasswordSetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.url_token = request.path[request.path.rfind('/') + 1:]
        email, parsed_datetime = decrypt_token(self.url_token)
        if is_verification_token_expired(parsed_datetime):
            return expired_response
        else:
            return super(PasswordSetView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.set_user_password(self.url_token)
        return super(PasswordSetView, self).form_valid(form)


class PasswordSetSuccess(TemplateView):
    template_name = "password_set_success.html"


###############################################################################
# Auth views
###############################################################################

class AuthLoginView(APIView):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def post(self, request: Request, *args, **kwargs):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            if PrefectureEmployee.objects.filter(user=user.id).exists():
                serializer_class = PrefectureEmployeeSerializer
                return_data = serializer_class(request.user.prefectureemployee).data
                return_data.update({'role': 'prefecture'})
            elif RegionEmployee.objects.filter(user=user.id).exists():
                serializer_class = RegionEmployeeSerializer
                return_data = serializer_class(request.user.regioneemployee).data
                return_data.update({'role': 'region'})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(data=return_data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class AuthLogoutView(APIView):

    def post(self, request: Request, format=None):
        logout(request)
        return Response(status=status.HTTP_200_OK)
