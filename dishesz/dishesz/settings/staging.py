



from .base import * 

BASE_DIR = Path(__file__).resolve().parent.parent


INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

host = AllowedHosts() 
host.add_host('scrapnc.com')
host.add_host('www.scrapnc.com')
host.add_host('18.191.137.57')


ALLOWED_HOSTS = host.get_allowed_hosts() 


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

CHANNEL_LAYERS = { 
    'default': { 
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': { 
            "hosts": ['redis://redis:6379']
        }
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






