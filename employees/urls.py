from django.conf.urls import url

from employees.views import PasswordSetView, PasswordSetSuccess, \
    AuthLoginView, AuthLogoutView

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
        AuthLoginView.as_view(),
        name='api_login'),
    url(r'^logout',
        AuthLogoutView.as_view(),
        name='api_logout'),
]
