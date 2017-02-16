from django.core.exceptions import ImproperlyConfigured

try:
    from .settings_local import *
except ImportError:
    raise ImproperlyConfigured('settings_local.py file not found!')
