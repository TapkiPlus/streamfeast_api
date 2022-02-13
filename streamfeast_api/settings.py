import os
import environ
from pathlib import Path

# READ ENV from Environment (+ .env file)
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# crucial settings
SITE_URL = env("TARGET_HOSTNAME")
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG", default=False)

# DB
DATABASES = {"default": env.db()}

# Email
EMAIL_CONFIG = env.email_url("EMAIL_CONFIG")
vars().update(EMAIL_CONFIG)

# Payment
PAYMENT_TEST_MODE = bool(env("PAYMENT_TEST_MODE"))
PAYMENT_MERCHANT_ID = env("PAYMENT_MERCHANT_ID")
PAYMENT_KEY = env("PAYMENT_KEY")

#==============================================#

# cors
CSRF_COOKIE_NAME = "csrftoken"
CORS_ORIGIN_ALLOW_ALL = True
ALLOWED_HOSTS = ['*']

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'be.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'standard',
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'db.log'),
            'when': 'midnight',
            'backupCount': 3,
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        'apscheduler.executors.default': {  # Stop spamming job scheduler logs
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': False
        },
        'django.request': {  # SQL logs go here
            'handlers': ['request_handler'],
            'level': 'WARN',
            'propagate': False
        }
    }
}

# middleware
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
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'template'],
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
TIME_ZONE = 'UTC'
DATETIME_FORMAT = 'd.m.Y H:i:s'
USE_I18N = True
USE_L10N = False
USE_TZ = False
ROOT_URLCONF = 'streamfeast_api.urls'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_UPLOAD_PATH = "uploads/"
