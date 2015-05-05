"""
Django settings for hawthorn project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.realpath(os.path.dirname(os.path.dirname(__file__))) 


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_p!o4c12#x3v8$cor#&vdpxddi1933e5q)9y0n@jp4@9es9!=d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ["dev.kirami.webfactional.com"]

#FORCE_SCRIPT_NAME = '/admin'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'audio',
    'django_extensions',
    'easy_thumbnails',
    #'south',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'hawthorn.urls'

WSGI_APPLICATION = 'hawthorn.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dev',
        'USER': 'kirami',
        'PASSWORD':'lfn1k1taWF',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Pacific'
USE_I18N = True
USE_L10N = True
USE_TZ = False

CA_TAX = 0.0975
ITEMS_PER_PAGE = 20

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'audio', 'templates'),
)


EMAIL_URL = "http://kirami.webfactional.com/audio/"

THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (50, 50), 'crop': True},
    },
}

STATICFILES_DIRS = (
    '/home/kirami/webapps/dev/hawthorn/static/',
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATIC_URL = 'http://dev.kirami.webfactional.com/static/'
STATIC_ROOT = '/home/kirami/webapps/static_dev/'
IMAGES_ROOT = STATIC_ROOT + "audio/images/"
IMAGES_URL = STATIC_URL + "audio/images"

LOGIN_URL = "/audio/accounts/login/"

MEDIA_ROOT = IMAGES_ROOT

EMAIL_URL = "http://dev.kirami.webfactional.com/audio/"
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'kirami'
EMAIL_HOST_PASSWORD = 'lfn1k1taWF'
DEFAULT_FROM_EMAIL = 'kirami@kirami.webfactional.com'
SERVER_EMAIL = 'kirami@kirami.webfactional.com'
EMAIL_PORT = 587

CA_TAX = 0.0975
ITEMS_PER_PAGE = 20


SHELL_PLUS_POST_IMPORTS = (

    ('audio.utils', '*'),
    ('audio.mail', '*'),
    ('audio.dropdowns', '*'),
    ('datetime', '*'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
    'verbose': {
    'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
    'datefmt' : "%d/%b/%Y %H:%M:%S"
    },
    'simple': {
        'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': '/home/kirami/webapps/dev/hawthorn/logs/debug.log',
        'formatter': 'verbose'
        },
    },
    'loggers': {
    'django': {
        'handlers':['file'],
        'propagate': True,
        'level':'INFO',
        },
        'audio': {
        'handlers': ['file'],
        'level': 'INFO',
        },
    }
}
