from django.conf.urls import url

from employees.views import PasswordSetView, PasswordSetSuccess

urlpatterns = [
    url(r'^success$',
        PasswordSetSuccess.as_view(),
        name='password_set_success'),
    url(r'^',
        PasswordSetView.as_view(),
        name='password_set'),
]
