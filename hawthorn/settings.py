"""
Django settings for hawthorn project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
PROJECT_PATH = os.path.realpath(os.path.dirname(os.path.dirname(__file__))) 

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'z5!kac$#pv4ox3bl$p)01&5@j0tr+(@z*srib1pcdg0_dc1a$m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ["haa", "anaplan-test"]

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/srv/messages'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'audio',
    'django_extensions',
    'django_requestlogging',
    #'django.contrib.sites',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'audio', 'templates'),
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_requestlogging.middleware.LogSetupMiddleware',
)

ROOT_URLCONF = 'hawthorn.urls'

WSGI_APPLICATION = 'hawthorn.wsgi.application'

#SITE_ID = 1

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hawthorn',
        'USER': 'root',
        'PASSWORD':'brandy1',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Pacific'

USE_I18N = True

USE_L10N = True

USE_TZ = False


SHELL_PLUS_POST_IMPORTS = (

    ('audio.utils', '*'),
    ('audio.mail', '*'),
    ('audio.dropdowns', '*'),
    ('datetime', '*'),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/srv/hawthorn/static/'
IMAGES_ROOT = STATIC_ROOT + "audio/images/"
IMAGES_URL = STATIC_URL + "audio/images"

LOGIN_URL = "/audio/accounts/login/"

MEDIA_ROOT = IMAGES_ROOT

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'kirajmd@gmail.com'
EMAIL_HOST_PASSWORD = 'lfn1k1taKD'

CA_TAX = 0.0975
ITEMS_PER_PAGE = 10


LOGGING = {
    "version":1,
    'disable_existing_loggers': True,
    'filters': {
        # Add an unbound RequestFilter.
        'request': {
            '()': 'django_requestlogging.logging_filters.RequestFilter',
        },
    },
    'formatters': {
        'request_format': {
            'format': '%(remote_addr)s %(username)s "%(request_method)s '
            '%(path_info)s %(server_protocol)s" %(http_user_agent)s '
            '%(message)s %(asctime)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['request'],
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/srv/hawthorn/logs/debug.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/srv/hawthorn/logs/error.log',
        },
    },
    'loggers': {
        'audio': {
            # Add your handlers that have the unbound request filter
            'handlers': ['file'],
            # Optionally, add the unbound request filter to your
            # application.
            'filters': ['request'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
         'django.request': {
            'handlers': ['error_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

