

import os
import django 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dishesz.settings')
django.setup() 

import channels.layers 
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from feeds.middleware import TokenAuthMiddlewareStack
from feeds.routing import websocket_urlpatterns 

application = ProtocolTypeRouter({ 
    'http': get_asgi_application(), 
    'websocket': TokenAuthMiddlewareStack( 
        URLRouter(websocket_urlpatterns)
    )
})

channel_layer = channels.layers.get_channel_layer() 