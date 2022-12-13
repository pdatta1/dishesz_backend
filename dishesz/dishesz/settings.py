

from datetime import timedelta
from pathlib import Path
from decouple import config 
import os 

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
ENV_NAME = config('ENV_NAME')
DEBUG = True

ALLOWED_HOSTS = ["scrapnc.com", "www.scrapnc.com", "18.191.137.57", "127.0.0.1", "testserver", "192.168.1.200"]
AUTH_USER_MODEL = 'users.DisheszUser'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users', 
    'recipe',
    'feeds',
    'notify',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders', 
    'storages',
    'channels',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'dishesz.urls'

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

WSGI_APPLICATION = 'dishesz.wsgi.application'
ASGI_APPLICATION = 'dishesz.asgi.application'

CHANNEL_LAYERS = { 
    'default': { 
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': { 
            "hosts": ['redis://redis:6379']
        }
    }
}


if ENV_NAME == 'staging-development': 


    DATABASES = {
        'default': {
            'ENGINE': config('DATABASE_ENGINE'),
            'NAME': config('DATABASE_NAME'),
            'USER': config('DATABASE_USER'),
            'PASSWORD': config('DATABASE_PASSWORD'),
            'HOST': config('DATABASE_HOST'), 
            'PORT': config('DATABASE_PORT'),
        }
    }


    CORS_REPLACE_HTTPS_REFERER      = True
    HOST_SCHEME                     = "https://"
    SECURE_PROXY_SSL_HEADER         = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT             = True
    SESSION_COOKIE_SECURE           = True
    CSRF_COOKIE_SECURE              = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
    SECURE_HSTS_SECONDS             = 1000000
    SECURE_FRAME_DENY               = True





if ENV_NAME == 'local-development': 

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }





REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication', 
    )
}

SIMPLE_JWT = { 
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# reset password lasts 10mins

PASSWORD_RESET_TIMEOUT = 600


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:3001',
    'http://192.168.1.200:3000',
    'http://192.168.1.200:3001',

]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# AWS CONFIG

AWS_ACCESS_KEY_ID = config('AWS_KEY')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET')
AWS_STORAGE_BUCKET_NAME = config('AWS_BUCKET_NAME')
AWS_QUERYSTRING_AUTH = False 
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' 


AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True


# EMAIL CONFIG

EMAIL_USE_TLS = True
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587





print(f'Current Env {ENV_NAME}')
