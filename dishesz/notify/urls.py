
from rest_framework.routers import DefaultRouter

from django.urls import path, include 
from notify.views import TestSendNotify

notify_router = DefaultRouter() 

notify_router.register(r'test_send_notify', TestSendNotify, basename='test_send_notify')

app_name = 'notify'
urlpatterns = [ 
    path('', include(notify_router.urls))
]