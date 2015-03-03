"""
Django settings for webui project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)  # so apps are importable when running scripts

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*a9)ea3*%0-wyglcw*0c9p3la6utvwf9mru%t)-xzw2tw#xlf1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangular',
    'corpus',
    'relatives',
    'relatedwidget',
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

SERIALIZATION_MODULES = {
    "underscore_resolution": "corpus.serializer",
}


ROOT_URLCONF = 'webui.urls'

WSGI_APPLICATION = 'webui.wsgi.application'

LOGIN_URL = '/admin/login'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join('/', 'tmp', 'db.sqlite3'),
    }
}

if 'test' in sys.argv or 'nosetests' in str(sys.argv):
    # No matter what, tests use ram-sqlite as database
    print('Using sqlite on memory as test database')
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False  # we dont need this feature


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django.db': {
            'level': 'WARNING',
            'propagate': True,
        },
    },
}


IEPY_LANG = 'en'
