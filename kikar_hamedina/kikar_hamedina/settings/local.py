from base import *

DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_STRING_IF_INVALID = "INVALID EXPRESSION: %s"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'from_backup',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost'
    }
}
