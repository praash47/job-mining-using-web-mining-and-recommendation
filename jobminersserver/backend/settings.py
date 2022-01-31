"""
Django settings for backend project.
"""

from pathlib import Path
CORS_ORIGIN_ALLOW_ALL = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1$esz!d!t6-%fdhnio)u&&fi##!8oy)+!ql#3=whviq)65&m#x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'checkers',
    'interactor',
    'jobdetailsextractor',
    'recommender',
    'requestutils',
    'tagprocessor',
    'timers',
    'channels',
    'django_eventstream',
    'corsheaders'
]

MIDDLEWARE = [
    'django_grip.GripMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'jobminers',
        'USER': 'jobminer',
        'PASSWORD': 'jobminer',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Channels
ASGI_APPLICATION = 'backend.asgi.application'

LOGGING = {
    'version': 1,
    'loggers': {
        'main': {
            'handlers': ['main'],
            'level': 'INFO'
        },
        'requestinggoogle': {
            'handlers': ['requestinggoogle'],
            'level': 'INFO',
        },
        'checkjobs': {
            'handlers': ['checkjobs'],
            'level': 'INFO',
        },
        'interactor': {
            'handlers': ['interactor'],
            'level': 'INFO',
        },
        'jobdetailsextractor': {
            'handlers': ['jobdetailsextractor'],
            'level': 'INFO',
        }
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s | %(module)s | %(funcName)s - %(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'main': {
            'class': 'logging.FileHandler',
            'filename': 'main.log',
            'formatter': 'default'
        },
        'requestinggoogle': {
            'class': 'logging.FileHandler',
            'filename': 'requestutils/requestgooglemodule/requestinggoogle.log',
            'formatter': 'default',
        },
        'checkjobs': {
            'class': 'logging.FileHandler',
            'filename': 'checkers/checkjobs.log',
            'formatter': 'default',
        },
        'interactor': {
            'class': 'logging.FileHandler',
            'filename': 'interactor/interactor.log',
            'formatter': 'default',
        },
        'jobdetailsextractor': {
            'class': 'logging.FileHandler',
            'filename': 'jobdetailsextractor/jobdetailsextractor.log',
            'formatter': 'default',
        }
    },
}

# Server Sent Events (django_eventstream settings)
EVENTSTREAM_ALLOW_ORIGIN = '*'
EVENTSTREAM_ALLOW_CREDENTIALS = True
EVENTSTREAM_ALLOW_HEADERS = 'Authorization'
