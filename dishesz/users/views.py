

from rest_framework.viewsets import ( 
    ReadOnlyModelViewSet, 
    ViewSet, 
)

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response 
from rest_framework import status 

from users.models import DisheszUser, DisheszUserFollowers, DisheszUserFollowing
from users.serializers import ( 
    DisheszUserSerializer, 
    ChangeEmailAddress, 
    ResetPasswordSerializer, 
    DisheszUserFollowersSerializer,
    DisheszUserFollowingSerializer
)
from users.verify import account_activation_token


from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes,  force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from decouple import config 


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
        
        return serialized_data.errors
    


    def create(self, request): 

        data = request.data 
        print(f'Data: {data}')
        new_user = self.create_user(data)
        print(f'New User Status : {new_user}')

          # if serialized valid
        if not new_user is None: 
            return Response(status=status.HTTP_201_CREATED, data={ 
                'message': f'Account Created, Verification Email Sent to {new_user["email"]}!'
            })
        return Response(status=status.HTTP_400_BAD_REQUEST, data={ 
            'message': 'Error Creating User'
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

    def list(self, request): 

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
       


    def create(self, request): 
        reset_data = self.send_password_reset_link(request.data['email'])
        return Response(status=status.HTTP_200_OK, data={
            'message': f'Email sent to {reset_data.username}',
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

    permission_classes = (IsAuthenticated, )

    def get_user_followers(self, user): 

        followers = DisheszUserFollowers.objects.filter(dishesz_user=user)
        serializer = DisheszUserFollowersSerializer(followers, many=True)
        return serializer.data 

    def list(self, request): 

        user_followers = self.get_user_followers(request.user) 
        return Response(status=status.HTTP_200_OK, data={ 
            'followers': user_followers
        })


class UserFollowingAPI(ViewSet): 

    permission_classes = (IsAuthenticated, )

    def get_user_followings(self, user): 
        
        followings = DisheszUserFollowing.objects.filter(dishesz_user=user)
        serializer = DisheszUserFollowingSerializer(followings, many=True)
        return serializer.data 


    def list(self, request): 

        user_followings = self.get_user_following(request.user)
        return Response(status=status.HTTP_200_OK, data={ 
            'followings': user_followings
        })




        


        



       










