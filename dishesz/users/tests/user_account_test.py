
from rest_framework.test import APITestCase
from rest_framework.test import force_authenticate
from rest_framework import status 


from django.urls import reverse 
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

import pytest 
import ast 

@pytest.mark.django_db
class TestUserAPI(APITestCase): 

    def setUp(self): 

        self.url = {
            'create_user': reverse('users:create_user-list'),
            'change_email': reverse('users:change_email-list'),
            'login_user': reverse('users:access'),
        }
        self.User = get_user_model().objects.create_user(username='admin', email='testing@gmail.com', password='password123')
    
    def test_retrieve_user_token(self): 

        data = { 
            'username': 'admin',
            'password': 'password123'
        }

        user = get_user_model().objects.get(username='admin')
        user.is_active = True 
        user.save() 

        self.client.force_login(user=user)

        request = self.client.post(self.url['login_user'], data)


        decode_dict = request.content.decode("UTF-8")
        token_dict = ast.literal_eval(decode_dict)

        token = token_dict["access"]

        if token is None: 
            raise ValueError(_('Token is None'))

        return token 
        

    def test_user_can_create_account(self): 

        data = { 
            'username': 'user11xx',
            'email': 'emailtest@gmail.com',
            'password': 'password123',
            'password2': 'password123'
        }
        request = self.client.post(self.url['create_user'], data, follow=True)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)


    
    def test_user_can_update_email(self): 

        data = { 
            "email": "cattabaah@gmail.com"
        }

        token = self.test_retrieve_user_token() 
        auth_header = { 
            'Authorization': f"Bearer {token}"
        }

        request = self.client.post(self.url['change_email'], data, follow=True, **auth_header)

        self.assertEqual(request.status_code, status.HTTP_200_OK)