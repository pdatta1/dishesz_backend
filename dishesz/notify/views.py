
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status 

from notify.core.send_notify import SendNotify

class TestSendNotify(ViewSet): 


    def create(self, request): 


        requested_user = request.user 
        notify_type = 'message'
        notify_data = { 
            'title': 'testing testing',
            'description': 'testing testing testing notification websocket',
            'reffered': 'following',
        }

        notify = SendNotify(requested_user.username)
        notify.send_notification(notify_type, notify_data)

        return Response(status=status.HTTP_201_CREATED, data={ 
            'data': notify_data,
            'type': notify_type
        })






