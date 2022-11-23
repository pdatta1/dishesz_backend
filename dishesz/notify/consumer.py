

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from notify.models import Notification

from django.utils.translation import gettext_lazy as _ 

class NotifyConsumer(AsyncJsonWebsocketConsumer): 

    def __init__(self, *args, **kwargs): 
        super().__init__(args, kwargs)

        self.notify_portal = [] 
        self.notify_portal_name = None 
        self.dishesz_user = None 


    async def connect(self): 

        # get the dishesz_user from the scope
        self.dishesz_user = self.scope['user']

        # if user is anonymous, close socket
        if self.dishesz_user.is_anonymous: 
            await self.close() 

        # if not, create portal name and load notifications
        else: 

            self.notify_portal_name = self.dishesz_user.username 
            await self.channel_layer.group_add(self.notify_portal_name, self.channel_name)

            viewed_notifications = await self.load_notifications(is_viewed=True)
            unviewed_notifications = await self.load_notification(is_viewed=False)

            self.notify_portal.append(viewed_notifications)
            self.notify_portal.append(unviewed_notifications)

            if not len(self.notify_portal[0]) == 0 or not len(self.notify_portal[1]) == 0: 

                await self.send_json({ 
                    'type': 'viewed.notification',
                    'data': self.notify_portal[0]
                })

                await self.send_json({ 
                    'type': 'unviewed.notification',
                    'data': self.notify_portal[1]
                })

    async def disconnect(self, code):
        return await super().disconnect(code)

    async def receive_json(self, content, **kwargs):
        
        notification_type = content.get('type')
        notification_data = content.get('data')

        if notification_type == 'notification.message': 
            notify_data = { 
                'type': notification_type,
                'data': notification_data
            }

            await self.channel_layer.group_send(self.notify_portal_name, notify_data)
            await self.create_notification(notification_data)


    
    async def viewed_notification(self, content): 
        await self.send_json({
            'type': content.get('type'),
            'data': content.get('data')
        })

    async def unviewed_notification(self, content): 
        await self.send_json({ 
            'type': content.get('type'),
            'data': content.get('data')
        })

    
    @database_sync_to_async
    def load_notifications(self, is_viewed): 

        container = [] 

        if self.dishesz_user is None: 
            raise ValueError()
        get_notifications = Notification.objects.filter(dishesz_user=self.dishesz_user, is_viewed=is_viewed)

        for data in get_notifications: 
            serialized_data = { 
                'title': data.title, 
                'description': data.description,
                'created_on': data.created_on, 
                'reffered': data.reffered,
                'dishesz_user': data.dishesz_user
            }
            container.append(serialized_data)
        return container 

    
    @database_sync_to_async
    def create_notification(self, data): 
        return Notification.objects.create(dishesz_user=self.dishesz_user, **data)



