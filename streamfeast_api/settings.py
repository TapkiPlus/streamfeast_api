import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SITE_URL = 'https://streamfest.ru'
BASE_URL = ''

SECRET_KEY = '$sgr9(w7g-5$1c=ip@0ex52rfyd$i5_8qtk28zi9nwy0br^23('

DEBUG = True

CSRF_COOKIE_NAME = "csrftoken"
CORS_ORIGIN_ALLOW_ALL = True
ALLOWED_HOSTS = ['*']

CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_UPLOAD_PATH = "uploads/"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'tickets@streamfest.ru'

# FIXME: set current password in production#
EMAIL_HOST_PASSWORD = '************'

DEFAULT_FROM_EMAIL = 'tickets@streamfest.ru'
EMAIL_USE_TLS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

INSTALLED_APPS = [
    'api.apps.AdminApiConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',

    'ckeditor',
    'api.apps.ApiConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'streamfeast_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'template']
        ,
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

WSGI_APPLICATION = 'streamfeast_api.wsgi.application'

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': 'test2',
        # 'USER' : 'root',
        # 'PASSWORD': 'i12345',
        # 'HOST': 'localhost', 
        # 'PORT': '3306'  
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'streamfest',
        'USER' : 'streamfest',
        'PASSWORD': 'J-I802kJ73nlDF832',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

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

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
DATETIME_FORMAT = 'd.m.Y H:i:s'
USE_I18N = True
USE_L10N = False
USE_TZ = False

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_URL = f'/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
