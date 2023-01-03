
"""

    @author: Patrick Atta-Baah 
    @file_name: send_notify.py
    @purpose: Handle Send Notification Message to websocket
    
"""

from channels.layers import get_channel_layer

from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth import get_user_model

from notify.models import Notification

from recipe.models import Recipe 


from asgiref.sync import async_to_sync



CHANNELS_TYPE = { 
    "viewed": "viewed.notification",
    "unviewed": "unviewed.notification",
    "message": "notification.message"
}



class SendNotify(object): 

    """
        SendNotify is responsible for establishing notification messages to the websocket.
    """

    def __init__(self, username): 
        """
            :param username: username to retrieved -> string
        """

        self.channel_layer = get_channel_layer() 
        self.requested_user = get_user_model().objects.get(username=username)


    def create_notification(self, **data): 
        """
            :param data: dict of data to be created
        """
        Notification.objects.create_notification(dishesz_user=self.requested_user, **data)


    def send_notification(self, data_type, data): 
        """
            :param type: data type notification content
            :param data: content data to be send
        """
        
        # validate data type in channels type dict
        if not data_type in CHANNELS_TYPE.values(): 
            raise ValueError(_('Invalid Type'))

        if self.channel_layer is None: 
            raise ValueError(_('Channel Layer is None'))

        
        portal_name = self.requested_user.get_username() 

        content_data = { 
            'type': data_type, 
            'data': data 
        }

        async_to_sync(self.channel_layer.group_send)(portal_name, content_data)

        self.create_notification(**data)


def handle_follow_notification( requested_user, recieved_user): 

    notify = SendNotify(recieved_user)
    notify_type = CHANNELS_TYPE['message']
    reffered_type = 'follower'

    notify_data = { 
        'title': f'got a new follower!',
        'description': f'{requested_user.username} is Following you',
        'reffered': reffered_type,
        'reffered_id': requested_user.id
    }

    notify.send_notification(notify_type, notify_data)
    



def handle_saves_notification( requested_user, recieved_user, recipe_id ): 



        notify = SendNotify(recieved_user)
        notify_type = CHANNELS_TYPE['message']
        reffered_type = 'review'

        recipe_data = Recipe.objects.get(id=recipe_id)

        notify_data = { 
            'title': 'new review',
            'description': f'{requested_user} left a review on {recipe_data.recipe_name}',
            'reffered': reffered_type,
            'reffered_id': recipe_id
        }

        notify.send_notification(notify_type, notify_data)



        
    