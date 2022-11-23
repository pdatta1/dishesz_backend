

from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from dishesz.dishesz.urls import urlpatterns


class RedirectFromAPI: 

    def __init__(self, get_response): 
        self.get_response = get_response

    def __call__(self, request): 

        pass 

