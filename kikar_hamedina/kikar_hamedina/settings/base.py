
import os
from os.path import dirname, abspath, join
from django.core.exceptions import ImproperlyConfigured

# return variable environment value or raise ImproperlyConfigured exception
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = 'Set the %s environment variable' % var_name
        raise ImproperlyConfigured(error_msg)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir))

sub_path = lambda *x: os.path.join(PROJECT_ROOT, *x)

# Configuring DATA_ROOT
DATA_ROOT = sub_path("data")

# Configuring MEDIA_ROOT
MEDIA_ROOT = sub_path("media")

# Configuring STATIC_ROOT
STATIC_ROOT = sub_path("collected_static")

# Additional locations of static files
STATICFILES_DIRS = (
    sub_path('static'),
)

# Configuring TEMPLATE_DIRS
TEMPLATE_DIRS = sub_path("templates")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('SECRET_KEY')

# SECURITY WARNING: keep the facebook app secret key used in production secret!
FACEBOOK_SECRET_KEY = get_env_variable('FACEBOOK_SECRET_KEY')

FACEBOOK_APP_ID = get_env_variable('FACEBOOK_APP_ID')

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'rest_framework',
    'django_extensions',
    'south',
    'pagination',
    'tagging',
    'planet',
    'persons',
    'knesset',
    'links',
    'video',
    'mks',
    'facebook_feeds',
    'core',
    'dj_facebook_realtime',
    'django.contrib.humanize',
    'endless_pagination',
    'dumpdata_chunks',
    'django_pandas'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "planet.context_processors.context",
    "core.context_processors.generic",
)

ROOT_URLCONF = 'kikar_hamedina.urls'

WSGI_APPLICATION = 'kikar_hamedina.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'kikar_hamedina',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost'
    }
}

LANGUAGE_CODE = 'he'

TIME_ZONE = 'Asia/Jerusalem'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

#Django-planet requirements
PLANET = {
    "USER_AGENT": "Kikar-Hamedina Planet/1.0"
}

SITE_ID = 1


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

LANGUAGE_COOKIE_NAME = "he"
SESSION_COOKIE_NAME = "myplanetid"


CURRENT_KNESSET_NUMBER = 19
