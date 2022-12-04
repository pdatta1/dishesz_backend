

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator


from django.utils.translation import gettext_lazy as _

from users.models import ( 
    DisheszUser, 
    DisheszUserProfile,
    DisheszUserFollowers, 
    DisheszUserFollowing, 
    InterestContainer, 
    Interest,

)


class DisheszUserProfileSerializer(ModelSerializer): 

    dishesz_user = serializers.ReadOnlyField(source='dishesz_user.username')
    profile_pic = serializers.ImageField()
    profile_status = serializers.ReadOnlyField() 

    class Meta: 
        model = DisheszUserProfile
        fields = ('dishesz_user', 'profile_pic', 'profile_status')
        

class DisheszUserFollowingSerializer(ModelSerializer): 

    user_follow = serializers.ReadOnlyField(source='user_follow.username')

    class Meta: 

        model = DisheszUserFollowing
        fields = ('user_follow', )


class DisheszUserFollowersSerializer(ModelSerializer): 

    follower = serializers.ReadOnlyField(source='follower.username')

    class Meta: 

        model = DisheszUserFollowers
        fields = ('follower', )

class InterestSerializer(ModelSerializer): 

    container = serializers.ReadOnlyField(source='container.dishesz_user.username')
    interest_name = serializers.CharField(allow_blank=False, max_length=24, min_length=5)
    interested_when = serializers.ReadOnlyField()

    class Meta: 
        model = Interest
        fields = ('container', 'interest_name', 'interested_when', )


class InterestContainerSerializer(ModelSerializer): 

    dishesz_user = serializers.ReadOnlyField(source='dishesz_user.username')
    interests = InterestSerializer(many=True)

    class Meta: 
        model = InterestContainer
        fields = ('dishesz_user', 'interests', )
    


class DisheszUserSerializer(ModelSerializer): 

    username = serializers.CharField(min_length=4, max_length=16, allow_blank=False, required=True, validators=[UniqueValidator(DisheszUser.objects.all())])
    email = serializers.EmailField(required=True, validators=[UniqueValidator(DisheszUser.objects.all())])

    password = serializers.CharField(min_length=8, max_length=24, write_only=True, required=True, allow_blank=False)
    password2 = serializers.CharField(min_length=8, max_length=24, write_only=True, required=True, allow_blank=False)

    #followings = DisheszUserFollowingSerializer(many=True)
    #followers = DisheszUserFollowersSerializer(many=True)
    #user_interest_container = InterestContainerSerializer()
    
    def validate(self, attrs): 

        if attrs['password'] != attrs['password2']: 
            raise ValueError(_('Password do not match!'))
        return attrs 

    def create(self, validated_data): 

        user = DisheszUser.objects.create_user(email=validated_data['email'], username=validated_data['username'], password=validated_data['password'])
        return user 


    class Meta: 

        model = DisheszUser
        fields = ('username', 'email', 'password', 'password2',)



class ChangeEmailAddress(ModelSerializer): 

    email = serializers.EmailField(required=True, allow_blank=False, validators=[UniqueValidator(DisheszUser.objects.all())])


    class Meta: 
        model = DisheszUser
        fields = ('email', )


class ResetPasswordSerializer(ModelSerializer): 

    password = serializers.CharField(min_length=5, max_length=24,  required=True, allow_blank=False)
    password2 = serializers.CharField(min_length=5, max_length=24, required=True, allow_blank=False)

    def validate(self, attrs): 

        if attrs['password'] != attrs['password2']: 
            raise ValueError(_('Password do not match!'))
        return attrs 


    class Meta: 
        model = DisheszUser
        fields = ('password', 'password2', )


