
from django.urls import path 
from django.utils.translation import gettext_lazy as _

from channels.generic.websocket import AsyncJsonWebsocketConsumer

class WebSocketRouting: 

    def __init__(self): 

        self.router = [] 


    def add_route(self, path_name, consumer): 

        if path_name is None: 
            raise ValueError(_('Path Name cannot be None'))
        
        if consumer is not type(AsyncJsonWebsocketConsumer): 
            raise ValueError(_('Consumer needs to be of type AsyncJsonWebsocketConsumer'))

        
        route =  path(path_name, consumer.as_asgi())
        self.router.append(route)

    def get_router(self): 
        return self.router 


