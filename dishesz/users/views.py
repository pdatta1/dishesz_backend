

from rest_framework.viewsets import ( 
    ReadOnlyModelViewSet, 
    GenericViewSet,
    ViewSet, 
)

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response 
from rest_framework import status 

from users.models import ( 
    DisheszUser, 
    DisheszUserFollowers, 
    DisheszUserFollowing, 
    DisheszUserProfile
)

from users.serializers import ( 
    DisheszUserSerializer, 
    ChangeEmailAddress, 
    ResetPasswordSerializer, 
    DisheszUserFollowersSerializer,
    DisheszUserFollowingSerializer, 
    DisheszUserProfileSerializer,
    InterestContainer,
    Interest
)
from users.verify import account_activation_token
from users.essentials import LookupUserProfileEssentials

from notify.core.send_notify import handle_follow_notification


from recipe.models import Recipe, SavedRecipes
from recipe.serializers import RecipeSerializer

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes,  force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.db.models import Q 

from decouple import config 
import random


def get_user(username):
    """
        get user model
        :param username: username to get user model by
    """
    user = get_user_model().objects.get(username=username)
    return user 

def get_authorized_frontend_url(): 
    return config('AUTHORIZED_FRONTEND')


def display_generic_green_status(message_value):
    """
         return generic 200 ok status code 
    """
    green_status_dict = {} 
    green_status = status.HTTP_200_OK

    green_status_dict['message'] = message_value
    green_status_dict['status'] = green_status

    return ( green_status_dict, green_status )


def display_generic_red_status(message_value): 
    """
        return generic 400 error status code
    """
    red_status_dict = {}
    red_status = status.HTTP_400_BAD_REQUEST

    red_status_dict['message'] = message_value
    

    return ( red_status_dict, red_status )
    
class DisheszUserAPI(ReadOnlyModelViewSet): 

    queryset = DisheszUser.objects.all() 
    serializer_class = DisheszUserSerializer
    permission_classes = (AllowAny, )



class CreateUserAPI(ViewSet): 

    permission_classes = (AllowAny, )
    ERROR = False 


    def send_verification_email(self, user): 
        """
            Sends the verification email to the user after account creation
            :param user: user to be sent to
        """

        if user is None: 
            raise ValueError(_('Dishesz User Cannot be None'))

        mail_subject = 'Activate Your Dishesz Account'
        message = render_to_string('users/email_verification.html', { 
            'domain': get_authorized_frontend_url,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        

        msg = EmailMultiAlternatives(mail_subject, "Verify Account!", to=[user.email])
        msg.attach_alternative(message, "text/html")
        msg.send()




    def create_user(self, user_data): 
        """
            create the user account and send verification email
            :param user_data: dictionary of data needed to create
                                user account
        """

        serialized_data = DisheszUserSerializer(data=user_data)
        if serialized_data.is_valid(): 
            serialized_data.save() 
            new_user = get_user(serialized_data.data['username'])
            self.send_verification_email(user=new_user)
            return serialized_data.data 
        
        self.ERROR = True 
        return serialized_data.error_messages
    


    def create(self, request): 

        data = request.data 
        #print(f'Data: {data}')
        
        new_user = self.create_user(data)
        #print(f'New User Status : {new_user}')

          # if serialized valid
        if not self.ERROR: 
            return Response(status=status.HTTP_201_CREATED, data={ 
                'message': f'Account Created, Verification Email Sent to {new_user["email"]}!'
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={ 
            'message': 'Error Creating User',
            'errors': new_user
        })
        

          
class VerifyEmail(ViewSet): 

    def get_user_from_email_verification_token(self, uidb64, token): 

        try: 

            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)

        except ( TypeError, ValueError, OverflowError, get_user_model().DoesNotExist): 
            return None 

        if user is not None and account_activation_token.check_token(user, token): 
            return user 
        return None 

    def create(self, request): 

        requested_data = request.data 
        _uid = requested_data['uid']
        _token = requested_data['token']

        user = self.get_user_from_email_verification_token(_uid, _token)

        if user:
            user.is_active = True 
            user.save() 
            return Response(status=status.HTTP_200_OK, data={ 
                'message': 'Account Verified!'
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "message": "verify Token expired"
        })



class ChangeEmailAPI(ViewSet): 

    permission_classes = (IsAuthenticated, )


    def change_email(self, user_data): 

        serializer = ChangeEmailAddress(data=user_data)
        if serializer.is_valid():
            user = get_user(self.request.user.username)
            user.email = serializer.data['email']
            user.save() 
            return user 

    def create(self, request): 

        handle_email = self.change_email(request.data)
        
        if handle_email is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': 'error changing email address'
            })
        return Response(status=status.HTTP_200_OK, data={
            'message': f'email address changed! {handle_email.email}'
        })



class HandleForgotPassword(ViewSet): 

    permission_classes = (AllowAny, )

    def send_password_reset_link(self, user_email): 
        """
            create a uid and token for the user 
            :param user_email: token and uid created by user_email
        """
        if user_email is None: 
            raise ValueError(_('Email required to reset password'))

        user = get_user_model().objects.get(email=user_email)

        current_site = get_current_site(self.request)
        mail_subject = 'Activate Your Dishesz Account'
        message = render_to_string('users/forgot_password.html', { 
            'domain': current_site.domain, 
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        

        msg = EmailMultiAlternatives(mail_subject, "This is a test!", to=[user.email])
        msg.attach_alternative(message, "text/html")
        msg.send()

        return user 

    def verify_email_exists(self, email): 

        if DisheszUser.objects.filter(email=email).exists(): 
            return True 
        return False 
       


    def create(self, request): 
        
        if self.verify_email_exists(request.data['email']): 
            reset_data = self.send_password_reset_link(request.data['email'])
            return Response(status=status.HTTP_200_OK, data={
                'message': f'Email sent to {reset_data.username}',
            })

        return Response(status=status.HTTP_400_BAD_REQUEST, data={ 
            'message': f'Dishesz cannot find an account with the email {request.data["email"]}'
        })


class ResetPasswordAPI(ViewSet): 

    permission_classes = (AllowAny, )

    def get_user_from_email_password_reset(self, uidb64, token): 
        """
            Get user from token and uid retrieve from requested data
            :param uidb64: uid retrieve to identify requested user
            :param token: token used to verify token activation
        """

        try: 

            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)

        except ( TypeError, ValueError, OverflowError, get_user_model().DoesNotExist): 
            return None 

        if user is not None and account_activation_token.check_token(user, token): 
            return user 
        return None 


    def reset_user_password(self, uidb64, token, password_data): 

        """
            reset user password
            :param password: user password to be changed
        """

        serializer = ResetPasswordSerializer(data=password_data)

        if serializer.is_valid():

            print(f'Serializer Data: {serializer.data}')
            user_account = self.get_user_from_email_password_reset(uidb64, token)
            if user_account:
                new_password = serializer.data['password']
                user_account.set_password(new_password)
                user_account.save() 
                return user_account


        return None 





    def create(self, request): 

        if request.data: 

            requested_data = request.data 

            print(f'Requested Data: {requested_data}')
            _token = requested_data['token']
            _uid = requested_data['uid']

            reset_handler = self.reset_user_password(_uid, _token, request.data)

            if reset_handler is None: 
                return Response(status=status.HTTP_400_BAD_REQUEST, data={ 
                    "message": "reset handler is None"
                })
            
            return Response(status=status.HTTP_200_OK, data={ 
                "message": f"Password have been reset for {reset_handler.username}"
            })

        return Response(status=status.HTTP_400_BAD_REQUEST, data={
                "message": "error resetting password"
            })
              



class DeleteAccountAPI(ViewSet): 

    permission_classes = (IsAuthenticated, )



    def delete_account(self, user): 
        
        _user_to_delete = get_user(username=user.username)
        if not _user_to_delete.is_active: 
            return None 

        _user_to_delete.delete()
        alert = { 'message': 'Account Deleted'}
        return alert 
            


    def create(self, request): 
        
        _user = request.user 
        _delete_user = self.delete_account(user=_user)
        if _delete_user is None: 
             return Response(status=status.HTTP_200_OK, data={
                'message': 'Error Delete User Account'
            })

        return Response(status=status.HTTP_200_OK, data=_delete_user)




class FollowUserAPI(ViewSet): 

    """
        This class allows user to follow their a certain user
    """

    permission_classes = (IsAuthenticated, )

    def follow_user(self, requested_user, user_to_follow):

        """
         :param user_to_follow: Dishesz User that will be followed
         :param user_following: Requested Dishesz User that enable the following
        """

        follow_container = {} 
        user_following_model = DisheszUserFollowing.objects.create(dishesz_user=requested_user, user_follow=user_to_follow)
        user_follower_model = DisheszUserFollowers.objects.create(dishesz_user=user_to_follow, follower=requested_user)

        follow_container['user_following'] = user_following_model.dishesz_user.username 
        follow_container['user_followed'] = user_follower_model.dishesz_user.username 

        return follow_container


    def eliminate_multiple_follows_per_user(self, requested_user, user_to_follow): 

        try: 
            check_following_model = DisheszUserFollowing.objects.get(dishesz_user=requested_user, user_follow=user_to_follow)
            if check_following_model: 
                return False 
        except DisheszUserFollowing.DoesNotExist: 
            return True 



    def create(self, request): 

        # get request data 
        requested_data = request.data 

        # get username from requested_data 
        followed_username = requested_data['username']
        
        # check if followed_username is None 
        if followed_username is None: 
            _dict, status  = display_generic_red_status('username is None')
            return Response(status=status, data=_dict)

        # get followed user 
        _followed_user = get_user(username=followed_username)

        # if user not followed follow user, if not return error 
        if self.eliminate_multiple_follows_per_user(request.user, _followed_user):

            _follow_intent = self.follow_user(request.user, _followed_user)
            handle_follow_notification(request.user, followed_username)

            _dict, status = display_generic_green_status(f'{_follow_intent["user_following"]} is Following {_follow_intent["user_followed"]}')
            return Response(status=status, data=_dict)

        _dict, status = display_generic_red_status(f'User is already Followed')
        return Response(status=status, data=_dict)



class unFollowUserAPI(ViewSet): 


    def unfollow_user(self, requested_user, user_to_unfollow): 
        """
            :param requested_user: user initializing the unfollow
            :param user_to_unfollow: user to unfollow
        """

        #
        user = get_user(user_to_unfollow)
        if user is None: 
            raise ValueError(_('User to Unfollow cannot be None'))


        try: 
            
            unfollow = DisheszUserFollowing.objects.get(dishesz_user=requested_user, user_follow=user)
            follower = DisheszUserFollowers.objects.get(dishesz_user=user, follower=requested_user)
            unfollow.delete() 
            follower.delete() 

        except DisheszUserFollowing.DoesNotExist: 
            raise ValueError(_('user do not exists to unfollow!'))


    def create(self, request): 

        requested_data = request.data 

        username = requested_data['username']

        if username is not None: 
            self.unfollow_user(request.user, username)
            _dict, status = display_generic_green_status('user unfollowed')
            return Response(status=status, data=_dict)

        _dict, status = display_generic_red_status('error unfollowing user')
        return Response(status=status, data=_dict)




class UserFollowersAPI(ViewSet): 

    """
        get all followers of requested user
    """

    permission_classes = (IsAuthenticated, )

    def get_user_followers(self, user): 

        """
            filter DisheszUserFollowers model with @param user
            serialized model and return serialized data 
        """

        followers = DisheszUserFollowers.objects.filter(dishesz_user=user)
        serializer = DisheszUserFollowersSerializer(followers, many=True)
        return serializer.data 

    def list(self, request): 

        user_followers = self.get_user_followers(request.user) 
        return Response(status=status.HTTP_200_OK, data={ 
            'followers': user_followers
        })


class UserFollowingAPI(ViewSet): 

    """
        get all followings of requested user 
    """

    permission_classes = (IsAuthenticated, )

    def get_user_followings(self, user): 
        """
            filter DisheszUserFollowing model with @param user
            serialize model and return serialized data
        """
        followings = DisheszUserFollowing.objects.filter(dishesz_user=user)
        serializer = DisheszUserFollowingSerializer(followings, many=True)
        return serializer.data 


    def list(self, request): 

        user_followings = self.get_user_followings(request.user)
        return Response(status=status.HTTP_200_OK, data={ 
            'followings': user_followings
        })


class CheckInterestPicked(ViewSet): 

    def check_user_interests(self): 

        container = InterestContainer.objects.get(dishesz_user=self.request.user)
        interests = Interest.objects.filter(container=container)

        if(interests): 
            return True 

    def check_profile_status(self): 

        user = get_user(self.request.user.username)
        profile = DisheszUserProfile.objects.get(dishesz_user=user)

        if self.check_user_interests(): 
            profile.profile_status = True 
            profile.save()
        else: 
            profile.profile_status = False 
            profile.save()  

        return profile.get_profile_status() 

    def list(self, request):

        _status = self.check_profile_status() 
        return Response(status=status.HTTP_200_OK, data={ 
            'status': _status 
        })


class InterestCollections(ViewSet): 


    def get_all_interests(self): 

        interests = Interest.objects.all() 
        for interest in interests: 
            yield interest.interest_name


    def list(self, request): 

        interests = list(self.get_all_interests())

        filter_duplicates_interests = set(interests) 
        return Response(status=status.HTTP_200_OK, data={ 
            'interests': filter_duplicates_interests
        })

        

class SuggestPeopleToFollow(GenericViewSet): 

    """
        This class is responsible of generating an algorithm based 
        on similar interests of users to follow
    """

    permission_classes = (IsAuthenticated, )


    def get_user_container(self): 
        """
            get container by requested user
            @return container 
        """
        container = InterestContainer.objects.get(dishesz_user=self.request.user)
        return container 


    def get_user_interest(self): 

        """
            assign container variable with get_user_container method, 
            filter all interests with assigned container variable

            loop thru interests objects and yield interest name 
        """
        container = self.get_user_container() 
        interests = Interest.objects.filter(container=container)

        if interests: 
            for interest in interests: 
                yield interest.interest_name




    
    def get_users_with_similar_interests(self): 

        """
            get all users with similar interests as of requested user.

            assign similar_interests variable to get_user_interest method -> generator to list convertion

            filter all users where InterestContainer of interest model of interest_name exists in similar interests list,
            and user cannot be of requested user 

            loop in users assigned list variable

            if user element isn't requested user of users list
                get user profile of user element, set response data dict, 
                and yield generate response_data
        """

        similar_interests = list(self.get_user_interest())

        # get all users

        users = DisheszUser.objects.filter(
            user_interest_container__interests__interest_name__in=similar_interests).filter(~Q(followings__dishesz_user=self.request.user))

        for user in users: 
            if not user == self.request.user:
                user_profile = DisheszUserProfile.objects.get(dishesz_user=user)
                response_data = { 
                    'username': user.username,
                    'user_id': user.id,
                    'profile_pic': user_profile.get_profile_pic_src(),
                }
                yield response_data



    def list(self, request): 

        """
            assign people_to_follow variable to get_users_with_similar_interests method -> generator  to list convertion
            get length of people_to_follow list

            if people_to_follow list length is None: 
                return response data of displaying 

            if  people_to_follow list length is either 1 or 2: 
                return response data of displaying

            if people_to_follow list length is greater than 2 and less than 10: 
                random sample people_to_follow list with max of 10 elements

            after all, 
                random sample people_to_follow list with max of 10 elements

            the last two steps are repetitive, but somehow works, so do not TOUCH!!!!
            without it it throw an exception. DO NOT TOUCH OR TRY TO REFACTOR THIS!!!!
        """

        people_to_follow = list(self.get_users_with_similar_interests())

        length_of_people = len(people_to_follow)

        if length_of_people == 0:
            return Response(status=status.HTTP_200_OK, data={
                'data': 'no usernames available to follow'
            })

        if length_of_people == 1 or length_of_people == 2: 
            return Response(status=status.HTTP_200_OK, data={
                'data': people_to_follow
            })

        if length_of_people > 2 and length_of_people <= 10: 
            max_people = 10
            max_display_people = random.sample(people_to_follow, max_people)
            return Response(status=status.HTTP_200_OK, data={
                'data': max_display_people
            })

        
        max_people = 10
        max_display_people = random.sample(people_to_follow, max_people)

        return Response(status=status.HTTP_200_OK, data={
            'data': max_display_people
        })



class LookupUserProfile(ViewSet): 

    def create(self, request): 

        """
            retrieve username from requested data,
            get user model from get_user method with params of retrieved username variable
            if username is not undefined or none 
            call serialized_response_data method to serialized reponse data of user model
            return response data with status 200
        """

        username = request.data["username"]
        user = get_user(username=username)

        essentials = LookupUserProfileEssentials()

        if username: 
            essentials.serialized_response_data(user_model=user)
            return Response(status=status.HTTP_200_OK, data={ 
                'user_profile': essentials.get_serialized_data()
            })



class MyProfileAPI(ViewSet): 

    """
        Displays requested user profile model
    """

    def get_user_profile(self): 

        profile = DisheszUserProfile.objects.get(dishesz_user=self.request.user)
        return profile 

    def serialize_user_profile(self): 

        profile = self.get_user_profile() 
        serializer = DisheszUserProfileSerializer(profile)
        return serializer.data 
    
    def list(self, request): 
        
        serializer = self.serialize_user_profile() 
        return Response(status=status.HTTP_200_OK, data={ 
            'profile': serializer
        })
