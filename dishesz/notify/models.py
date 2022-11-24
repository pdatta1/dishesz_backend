from django.db import models
from django.utils import timezone


REFFERED_CHOICES = ( 

    (1, 'follow request'), 
    (2, 'following'), 
    (3, 'saved recipe'),
)

class Notification(models.Model): 
    """
        This class is responsible storaging the models of a requested user
        notifications
    """


    title = models.CharField(max_length=24, blank=False, null=False)
    description = models.CharField(max_length=128, blank=False, null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    reffered = models.CharField(max_length=16, choices=REFFERED_CHOICES)
    is_viewed = models.BooleanField(default=False)
    dishesz_user = models.ForeignKey(to='users.DisheszUser', on_delete=models.CASCADE, related_name='user_notifications')

    