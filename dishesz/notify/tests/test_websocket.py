
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import AccessToken

from dishesz.asgi import application

import pytest 

TEST_CHANNEL_LAYERS = { 
    'default': { 
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}


@database_sync_to_async
def create_user(username, email, password):

    user = get_user_model().objects.create_user(username=username, email=email, password=password)
    user.is_active = True 
    user.save() 

    access = AccessToken.for_user(user)
    return user, access 


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestWebSocketConnection(object): 

    async def get_user_access(self): 

        _, access = await create_user('user_test', 'user_test@gmail.com', 'user_test123')
        return access

    async def test_can_connect_to_server(self, settings): 

        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        access = await self.get_user_access() 

        communicator = WebsocketCommunicator(
            application=application, 
            path=f'/ws/notify/?token={access}'
        )

        connected, _ = await communicator.connect() 
        assert connected is True 
        await communicator.disconnect() 


    async def test_cannot_connect_without_token(self, settings):

        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

        communicator = WebsocketCommunicator(
            application=application,
            path=f'/ws/notify/'
        )

        connected, _ = await communicator.connect()

        assert connected is False 
        await communicator.disconnect() 


    async def test_can_send_and_receive_message(self, settings): 

        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        access = await self.get_user_access() 

        communicator = WebsocketCommunicator(
            application=application,
            path=f'/ws/notify/?token={access}'
        )

        await communicator.connect()

        message = { 
            'type': 'echo.message',
            'data': 'this is a test'
        }

        await communicator.send_json_to(message)

        response = await communicator.receive_json_from() 

        assert response ==  message 
        await communicator.disconnect()









