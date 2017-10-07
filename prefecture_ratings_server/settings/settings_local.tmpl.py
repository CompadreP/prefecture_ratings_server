from corsheaders.defaults import default_headers

from .settings import *

DEBUG = True

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'app/static')

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'app/media')

ALLOWED_HOSTS = ['*']

SECRET_KEY = 'stub'

SECRET_FERNET_KEY = b'RumPr2Mc4c1oti9i0N9ck876zbt12YIrbU5lLMp9lDA='

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '--name--',
        'USER': '--user--',
        'PASSWORD': '--password--',
        'HOST': '--host--',
        'PORT': '--port--',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        'TIMEOUT': None,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CORS_ORIGIN_WHITELIST = (
    'localhost:4200',
    'localhost:4200/',
    'localhost',
    '127.0.0.1:4200',
    '127.0.0.1:4200/',
    '127.0.0.1'
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = default_headers

