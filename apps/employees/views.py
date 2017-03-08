import datetime

from django.conf import settings
from django.contrib.auth import login, logout
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.contrib.auth import authenticate
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.employees.common import decrypt_token
from apps.employees.forms import PasswordSetForm
from apps.employees.models import RegionEmployee, PrefectureEmployee, RatingsUser
from apps.employees.serializers import PrefectureEmployeeDetailSerializer, \
    RegionEmployeeSerializer, PrefectureEmployeeSimpleSerializer, \
    RatingsUserSerializer

###############################################################################
# Password set views (standard django)
###############################################################################
from apps.employees.tasks import generate_token_and_send_email


def is_verification_token_expired(parsed_datetime: datetime.datetime):
    if (datetime.datetime.now() - parsed_datetime) \
            > datetime.timedelta(seconds=settings.PASSWORD_SET_FORM_TTL_SECONDS):
        return True
    else:
        return False


def expired_response(request):
    return TemplateResponse(request, "password_set_expired.html")


class PasswordSetSuccess(TemplateView):
    template_name = "password_set_success.html"


class PasswordSetView(FormView):
    template_name = "password_set_form.html"
    form_class = PasswordSetForm
    success_url = '/password_set/success'

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        url_token = request.path[request.path.rfind('/') + 1:]
        _, parsed_datetime = decrypt_token(url_token)
        if is_verification_token_expired(parsed_datetime):
            return expired_response(request)
        else:
            return super(PasswordSetView, self).get(request, *args, **kwargs)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        self.url_token = request.path[request.path.rfind('/') + 1:]
        email, parsed_datetime = decrypt_token(self.url_token)
        if is_verification_token_expired(parsed_datetime):
            return expired_response(request)
        else:
            return super(PasswordSetView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.set_user_password(self.url_token)
        return super(PasswordSetView, self).form_valid(form)


class PasswordResetView(PasswordSetView):

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        url_token = request.path[request.path.rfind('/') + 1:]
        email, parsed_datetime = decrypt_token(url_token)
        if is_verification_token_expired(parsed_datetime):
            return expired_response(request)
        else:
            RatingsUser.objects.get(email=email).set_unusable_password()
            return super(PasswordSetView, self).get(request, *args, **kwargs)


###############################################################################
# Auth views
###############################################################################

class LoginView(APIView):

    @method_decorator(csrf_protect)
    def post(self, request: Request, *args, **kwargs):
        try:
            email = request.data['email']
            password = request.data['password']
        except KeyError:
            return Response(
                data={'detail': 'no_user_credentials_provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            if PrefectureEmployee.objects.filter(user=user.id).exists():
                return_data = PrefectureEmployeeDetailSerializer(request.user.prefectureemployee).data
                return_data.update({'role': 'prefecture'})
            elif RegionEmployee.objects.filter(user=user.id).exists():
                return_data = RegionEmployeeSerializer(request.user.regionemployee).data
                return_data.update({'role': 'region'})
            elif user.is_admin:
                user_data = RatingsUserSerializer(request.user).data
                return_data = {'user': user_data}
                return_data.update({'role': 'admin'})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(data=return_data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class LogoutView(APIView):

    @method_decorator(ensure_csrf_cookie)
    def post(self, request: Request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class ResetPasswordRequestView(APIView):

    # TODO throttling
    @method_decorator(csrf_protect)
    def post(self, request: Request, *args, **kwargs):
        email = request.data['email']
        subject = 'Сброс пароля аккаунта на сайте prefecture-ratings.ru'
        body = ('Кто-то (возможно не вы) запросил сброс пароля вашего аккаунта.'
                '\n\nЕсли это были не вы, то просто проигнорируйте данное письмо.'
                '\n\nЧтобы сбросить пароль и установить новый, перейдите по ссылке - {base_url}/password_set/{url_token}.'
                '\n\nСсылка действительна в течении 24 часов.')
        generate_token_and_send_email(email, subject, body)
        return Response(status=status.HTTP_200_OK)


###############################################################################
# Employees
###############################################################################

class PrefectureEmployeesViewSet(GenericViewSet,
                                 mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin):
    queryset = PrefectureEmployee.objects.filter(user__is_active=True)
    serializer_class = PrefectureEmployeeSimpleSerializer
    permission_classes = (AllowAny, )

    @method_decorator(ensure_csrf_cookie)
    def list(self, request: Request, *args, **kwargs):
        include_approvers = request.GET.get('include_approvers')
        queryset = self.filter_queryset(self.get_queryset())
        if not include_approvers:
            queryset = queryset.filter(can_approve_rating=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
