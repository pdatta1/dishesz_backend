

from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import DisheszUser, DisheszUserProfile

@receiver(post_save, sender=DisheszUser)
def create_user_profile(sender, instance, created, **kwargs): 
    
    if created: 
        DisheszUserProfile.objects.create(dishesz_user=instance)

