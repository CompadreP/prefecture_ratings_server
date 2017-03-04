"""prefecture_ratings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from apps.employees.urls import password_set_urlpatterns, \
    authentication_urlpatterns, password_reset_urlpatterns, \
    employees_urlpatterns


admin.site.site_header = 'Администрирование'


@ensure_csrf_cookie
def main_page(request, *args, **kwargs):
    return HttpResponse()


urlpatterns = [
    url(r'^api/ratings/', include('apps.ratings.urls')),
    url(r'^api/map/', include('apps.map.urls')),
    url(r'^api/employees/', include(employees_urlpatterns)),
    url(r'^api/auth/', include(authentication_urlpatterns)),
    url(r'^$', main_page, name='main_page'),
    url(r'^admin/', admin.site.urls),
    url(r'^password_set/', include(password_set_urlpatterns)),
    url(r'^forgot_password/', include(password_reset_urlpatterns)),
]
