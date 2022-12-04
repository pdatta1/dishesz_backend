

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone 

from users.manager import DisheszUserManager
from recipe.utils import photo_path

from decouple import config 



class DisheszUser(AbstractBaseUser, PermissionsMixin): 
    """"
        Defining the Custom DisheszUser Model which implements the AbstractBaseUser and PermissionsMixins
    """

    # required data 
    username = models.CharField(max_length=16, blank=False, null=False, unique=True)
    email = models.EmailField(blank=False, null=False, unique=True)


    # account_status | staff data
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # core 
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'
    objects = DisheszUserManager() 


class DisheszUserProfile(models.Model): 

    """
        Defining the DisheszUserProfile which consists of the user profile pic, date of birth and etc.
    """
    dishesz_user = models.OneToOneField(to=DisheszUser, on_delete=models.CASCADE, related_name='user_profile')
    profile_pic = models.ImageField(upload_to=f'profile/{photo_path}')
    profile_status = models.BooleanField(default=False)

    def get_profile_status(self): 
        return self.profile_status 

    def get_profile_pic_src(self): 
        if not self.profile_pic: 
            return config('DEFAULT_USER_PROFILE_PIC')
        return self.profile_pic.url 

    def __str__(self): 
        return f'{self.dishesz_user.username} Profile'


class DisheszUserFollowing(models.Model): 
    """
        Defining the DisheszUserFollowing Model which stores all
        of the users that is been followed
    """
    
    dishesz_user = models.ForeignKey(DisheszUser, on_delete=models.CASCADE, related_name='followings')
    user_follow = models.ForeignKey(DisheszUser, on_delete=models.CASCADE)
    following_when = models.DateTimeField(auto_now_add=True, null=True) # change null to False after initialize staging deployment


    def __str__(self): 
        return f'{self.dishesz_user} Following {self.user_follow}'


class DisheszUserFollowers(models.Model): 
    """"
        Defining the DisheszUserFollowers Model which stores all 
        of the user's followers
    """
    
    dishesz_user = models.ForeignKey(DisheszUser, on_delete=models.CASCADE, related_name='followers')
    follower = models.ForeignKey(DisheszUser, on_delete=models.CASCADE)
    followed_when = models.DateTimeField(auto_now_add=True, null=True) # change null to False after initialize staging deployment

    
    def __str__(self): 
        return f'{self.follower} is a Follower to {self.dishesz_user}'




class InterestContainer(models.Model): 
    """
        Defining the InterestContainer Model which consists of all of the user interests
    """

    dishesz_user = models.OneToOneField(DisheszUser, on_delete=models.CASCADE, related_name='user_interest_container')

class Interest(models.Model): 

    """"
        Defining the Interest Container Model 
        which consists of the interest
    """

    container = models.ForeignKey(InterestContainer, on_delete=models.CASCADE, related_name='interests')
    interest_name = models.CharField(max_length=24, null=False, blank=False)
    interested_when = models.DateTimeField(auto_now_add=True)