

from .base import * 


DEBUG = True 

INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

INTERNAL_IPS = [ 
    '127.0.0.1'
]

host = AllowedHosts() 
host.add_host('scrapnc.com')
host.add_host('www.scrapnc.com')
host.add_host('18.191.137.57')
host.add_host('127.0.0.1')
host.add_host('testserver')
host.add_host('192.168.1.200')

ALLOWED_HOSTS = host.get_allowed_hosts() 


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CHANNEL_LAYERS = { 
    'default': { 
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': { 
            'hosts': [('127.0.0.1', 6379)],
        }
        
    }
}





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






