


from django.db import models 
from django.utils.translation import gettext_lazy as _ 



class NotificationManager(models.Manager): 

    
    def create_notification(self, dishesz_user, **extra_data): 

        notification = self.create(dishesz_user=dishesz_user, **extra_data)
        return notification 

    def get_all_notifications(self): 

        notifications = self.all() 
        return notifications

    def get_user_notifications(self, dishesz_user): 

        notifications = self.filter(dishesz_user=dishesz_user)
        return notifications

    def get_user_notification_by(self, dishesz_user, viewed): 

        notification = self.filter(dishesz_user=dishesz_user, is_viewed=viewed)
        return notification

    
    def get_user_notification_by_creation(self, dishesz_user, sort_sequence): 

        notifications = None 
        if sort_sequence == 'first': 
            notifications = self.filter(dishesz_user=dishesz_user).order_by('created_on')
            return notifications

        if sort_sequence == 'last': 
            notifications = self.filter(dishesz_user=dishesz_user).order_by('created_on')[::-1]
            return notifications

    

