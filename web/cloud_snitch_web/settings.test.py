"""
Django settings for cloud_snitch_web project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your_secret_key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    '*',
]


# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'neo4jdriver',
    'web.apps.WebConfig',
    'common.apps.CommonConfig',
    'api.apps.ApiConfig',
    # 'raxauth'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', #  Normal db auth
    # 'raxauth.middleware.AuthenticationMiddleware', #  Auth from rackspace
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cloud_snitch_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cloud_snitch_web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db', 'db.sqlite3'),
    }
}

NEO4J = {
    'username': "neo4j_username",
    'password': "neo4j_password",
    'uri': "bolt://neo4j_uri",
    'max_connection_lifetime':  300,
    'max_connection_pool_size': 50,
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/opt/web/cloud_snitch/web/static'

CELERY_RESULT_BACKEND = 'django-cache'
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_BROKER_TRANSPORT_OPTIONS = {'socket_timeout': 60}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

SESSION_CACHE_ALIAS = 'sessions'
SESSION_TIMEOUT = 3600
SESSION_ENGINE = "django.contrib.sessions.backends.file"

CSRF_COOKIE_NAME = '_cloud_snitch_csrf_cookie_'

DEFAULT_CACHE_TIMEOUT = 30


LOGGING = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console']
        },
        'api': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'neo4jdriver': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'api.query': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'neo4j.bolt': {
            'level': 'ERROR',
            'handlers': ['console']
        }
    }
}

# LOGIN_URL = '/raxauth/login/' #  RAX AUTH
LOGIN_URL = '/web/login/' #  DB AUTH


LOGIN_REDIRECT_URL = '/web/'

# AUTH_USER_MODEL = 'raxauth.RaxAuthUser' #  RAX AUTH
# AUTHENTICATION_BACKENDS = [ # RAX AUTH
#    'raxauth.backend.RaxAuthBackend' #  RAX AUTH
# ] # RAX AUTH

# RAXAUTH_AUTH_URL = 'https://someurl.com' #  RAX AUTH

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}
