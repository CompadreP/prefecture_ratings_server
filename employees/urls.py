from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from employees.views import PasswordSetView, PasswordSetSuccess, \
    LoginView, LogoutView, PasswordResetView, ResetPasswordRequestView, \
    PrefectureEmployeesViewSet

password_set_urlpatterns = [
    # password set
    url(r'^success$',
        PasswordSetSuccess.as_view(),
        name='password_set_success'),
    url(r'^',
        PasswordSetView.as_view(),
        name='password_set'),
]

password_reset_urlpatterns = [
    url(r'^',
        PasswordResetView.as_view(),
        name='password_reset'),
]

authentication_urlpatterns = [
    url(r'^login',
        LoginView.as_view(),
        name='api_login'),
    url(r'^logout',
        LogoutView.as_view(),
        name='api_logout'),
    url(r'^reset_password',
        ResetPasswordRequestView.as_view(),
        name='api_reset_password_request'),
]

router = DefaultRouter()
router.register(r'prefecture_employees', PrefectureEmployeesViewSet)
employees_urlpatterns = router.urls
