import os
from importlib import import_module

from celery import Celery

settings = import_module(os.environ['DJANGO_SETTINGS_MODULE'])
app = Celery('emails',
             config_source=settings.CELERY_CONFIG)
