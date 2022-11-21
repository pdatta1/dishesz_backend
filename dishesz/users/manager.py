

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _ 



class DisheszUserManager(BaseUserManager): 
    """
        Handles DisheszUser
    """


    def create_user(self, email, password, **extra_fields): 

        if not email: 
            raise ValueError(_('Email is needed!'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save() 
        
        return user 


    def create_admin(self, email, password, **extra_fields): 

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)


        if not extra_fields.get('is_superuser') is True: 
            raise ValueError(_('Admin needs super powers!'))
        
        if not extra_fields.get('is_staff') is True: 
            raise ValueError(_('Admin needs staff privileges'))

        return self.create_user(email=email, password=password, **extra_fields)