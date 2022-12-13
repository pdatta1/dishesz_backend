
from rest_framework.test import APITestCase
from rest_framework import status 


from django.urls import reverse 
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str

from users.verify import account_activation_token

import pytest 

@pytest.mark.django_db
class TestUserAPI(APITestCase): 

    def setUp(self): 

        self.url = {
            'create_user': reverse('users:create_user-list'),
            'change_email': reverse('users:change_email-list'),
            'login_user': reverse('users:access'),
            'forgot_password': reverse('users:handle_forgot_password-list'),
            'reset_password': reverse('users:reset_password-list'),
            'verify_email': reverse('users:verify-list'),
            'handle_forgot_password': reverse('users:handle_forgot_password-list'),
            'delete_account': reverse('users:delete_account-list'),
            'follow_user': reverse('users:follow_user-list'),
            'unfollow_user': reverse('users:unfollow_user-list'),
            'user_followers': reverse('users:user_followers-list'),
            'user_followings': reverse('users:user_followings-list')

        }
        self.User = get_user_model().objects.create_user(username='admin', email='testing@gmail.com', password='password123')
    

    """
        Login and Create Account Testing
    """
    def test_retrieve_user_token(self): 

        data = { 
            'username': 'admin',
            'password': 'password123'
        }

        user = get_user_model().objects.get(username='admin')
        user.is_active = True 
        user.save() 

        self.client.force_login(user=user)

        request = self.client.post(self.url['login_user'], data, follow=True)


        #decode_dict = json.loads(request.content.decode("UTF-8"))
        token = request.data["access"]

        if token is None: 
            raise ValueError(_('Token is None'))

        return token 

    def test_initialize_auth_headers(self):

        token = self.test_retrieve_user_token() 
        auth_headers = { 
            'Authorization': f'Bearer {token}'
        }

        return auth_headers
        

    def test_user_can_create_account(self): 

        data = { 
            'username': 'user11xx',
            'email': 'emailtest@gmail.com',
            'password': 'password123',
            'password2': 'password123'
        }
        request = self.client.post(self.url['create_user'], data, follow=True)

        new_user = get_user_model().objects.get(username=data['username'])


        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['username'], new_user.username)
        self.assertEqual(data['email'], new_user.email)
        self.assertEqual(False, new_user.is_active)
        self.assertEqual(False, new_user.is_superuser)
        self.assertEqual(False, new_user.is_staff)


    def test_user_create_with_existing_email(self): 

        data = { 
            'username': 'user123', 
            'email': 'testing@gmail.com', 
            'password': 'password123', 
            'password2': 'password123'
        }

        request = self.client.post(self.url['create_user'], data, follow=True)
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)


    def test_user_create_with_invalid_email(self): 


        data = { 
            'username': 'user123', 
            'email': 'testinggmail.com', 
            'password': 'password123', 
            'password2': 'password123'
        }

        request = self.client.post(self.url['create_user'], data, follow=True)
        
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)


    def test_user_create_with_short_username(self): 

        data = { 
            'username': 'use', 
            'email': 'testing@gmail.com', 
            'password': 'password123', 
            'password2': 'password123'
        }

        request = self.client.post(self.url['create_user'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_create_with_short_password(self): 

        data = { 
            'username': 'use', 
            'email': 'testing@gmail.com', 
            'password': 'pass123', 
            'password2': 'pass123'
        }

        request = self.client.post(self.url['create_user'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_user_create_with_unmatch_password(self): 

        data = { 
            'username': 'use', 
            'email': 'testing@gmail.com', 
            'password': 'password123', 
            'password2': 'password123'
        }

        request = self.client.post(self.url['create_user'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)


    """
        Patching Email Testing.
    """
    
    def test_user_can_update_email(self): 

        data = { 
            "email": "cattabaah@gmail.com"
        }

        auth_header = self.test_initialize_auth_headers() 
        request = self.client.post(self.url['change_email'], data, follow=True, **auth_header)

        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_user_can_receive_forgotten_password_email(self): 

        data = { 
            "email": "testing@gmail.com"
        }

        request = self.client.post(self.url['forgot_password'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_200_OK)

    
    def test_user_cannot_receieve_with_nonexisting_email(self): 

        data  = { 
            "email": "cattabaah@gmail.com"
        }

        request = self.client.post(self.url['forgot_password'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)


    """
        Password Reset Testing
    """

    def generate_user_token(self, user): 

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            return uid, token 
        

    def generate_user_password_token(self, user): 

        
        uid, token = self.generate_user_token(user) 

        data = { 
            'uid': uid,
            'token': token,
            'password': 'password9999',
            'password2': 'password9999'
        }

        return data 


    def get_tested_user(self): 

        user = get_user_model().objects.get(username='admin')
        user.is_active = True 
        user.save() 

        return user     

    def test_user_can_reset_password(self): 


        user = self.get_tested_user() 

        data = self.generate_user_password_token(user) 
        request = self.client.post(self.url['reset_password'], data, follow=True)

        decoded_user_from_uid = force_str(urlsafe_base64_decode(data['uid']))
        decoded_user = get_user_model().objects.get(pk=decoded_user_from_uid)
        check_token = account_activation_token.check_token(user=decoded_user, token=data['token'])

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(user, decoded_user)
        self.assertEqual(True, check_token)


    def test_user_can_send_forgotten_password_request(self): 
        
        data = { 
            "email": "testing@gmail.com"
        }

        request = self.client.post(self.url['handle_forgot_password'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_200_OK)


    def test_user_non_existing_email_to_reset_password(self): 

        data = { 
            "email": "testing123@gmail.com"
        }

        request = self.client.post(self.url['handle_forgot_password'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)


    def test_invalid_email_to_reset_password(self): 

        data = { 
            "email": "testing"
        }

        request = self.client.post(self.url['handle_forgot_password'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)

    

    """
        Verify User Test 
    """

    def test_user_can_verify(self): 

        user = self.get_tested_user() 
        uid, token = self.generate_user_token(user) 

        data = { 
            'uid': uid, 
            'token': token 
        }

        request = self.client.post(self.url['verify_email'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_200_OK)

    """"
        Delete User Account Test 
    """
    def test_user_can_delete_account(self): 

        header = self.test_initialize_auth_headers() 

        request = self.client.post(self.url['delete_account'], **header)

        self.assertEqual(request.status_code, status.HTTP_200_OK)



    """
        User Following Test 
    """

    def get_tested_followed_user(self): 

        followed_user = get_user_model().objects.create_user(username='follow_user', email='following@gmail.com', password='follow123')
        followed_user.is_active = True 
        followed_user.save() 

        return followed_user

    def test_user_can_follow(self):

        auth_headers = self.test_initialize_auth_headers() 
        user_to_follow = self.get_tested_followed_user() 

        data = { 
            'username': user_to_follow.username
        }

        request = self.client.post(self.url['follow_user'], data, follow=True, **auth_headers)

        self.assertEqual(request.status_code, status.HTTP_200_OK)


    def test_unfollow_user(self): 

        auth_headers = self.test_initialize_auth_headers() 
        user_to_follow = self.get_tested_followed_user() 
        data = { 
            'username': user_to_follow.username
        }

        request = self.client.post(self.url['follow_user'], data, follow=True, **auth_headers)
        unfollow_request = self.client.post(self.url['unfollow_user'], data, follow=True, **auth_headers)

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(unfollow_request.status_code, status.HTTP_200_OK)


    def test_user_cannnot_follow_or_unfollow_anonymous(self): 

        user_to_follow = self.get_tested_followed_user() 
        data = { 
            'username': user_to_follow.username
        }

        request = self.client.post(self.url['follow_user'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_get_user_followers(self): 

        auth_headers = self.test_initialize_auth_headers()  

        request = self.client.get(self.url['user_followers'], follow=True, **auth_headers)

        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_cannot_get_followers_anonymous(self): 

        request = self.client.get(self.url['user_followers'], follow=True)

        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_get_followings_anonymous(self): 

        request = self.client.get(self.url['user_followings'], follow=True)

        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

        

    


    
