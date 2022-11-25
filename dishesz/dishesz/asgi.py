

import os
import django 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dishesz.settings')
django.setup() 

import channels.layers 
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from middlewares.auth_websocket import TokenAuthMiddlewareStack 

from websocket_routing.routing import WebSocketRouting
from notify.consumer import NotifyConsumer

# intialize websocket routing and add consumers
websocket_router = WebSocketRouting() 
websocket_router.add_route('ws/notify/', NotifyConsumer)

application = ProtocolTypeRouter({ 
    'http': get_asgi_application(), 
    'websocket': TokenAuthMiddlewareStack( 
        URLRouter(websocket_router.get_router())
    )
})

channel_layer = channels.layers.get_channel_layer() 