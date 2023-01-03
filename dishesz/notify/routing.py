
from django.urls import path 
from notify.consumer import NotifyConsumer


notify_urlpatterns = [ 
    path('ws/notify/', NotifyConsumer.as_asgi())
]