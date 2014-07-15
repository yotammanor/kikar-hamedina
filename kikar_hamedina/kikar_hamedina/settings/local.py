from base import *

DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_STRING_IF_INVALID = "INVALID EXPRESSION: %s"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'kikar_hamedinai.db',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost'
    }
}
