from base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'kikar',
        'USER': 'kikar',
        'PASSWORD': 'kikar',
        'HOST': 'localhost'
    }
}

ALLOWED_HOSTS = [
    '95.85.54.42',
    '95.85.54.42:8000',
    'kikar.hasadna.org.il'
]