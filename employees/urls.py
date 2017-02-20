from django.conf.urls import url

from employees.views import PasswordSetView, PasswordSetSuccess, \
    LoginView, LogoutView

password_set_urlpatterns = [
    # password set
    url(r'^success$',
        PasswordSetSuccess.as_view(),
        name='password_set_success'),
    url(r'^',
        PasswordSetView.as_view(),
        name='password_set'),
]

authentication_urlpatterns = [
    url(r'^login',
        LoginView.as_view(),
        name='api_login'),
    url(r'^logout',
        LogoutView.as_view(),
        name='api_logout'),
]
