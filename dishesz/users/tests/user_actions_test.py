
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework import status 


from django.urls import reverse
from django.shortcuts import reverse 
from django.contrib.auth import get_user_model

import pytest 

@pytest.mark.django_db
class TestUserAPI(APITestCase): 

    def setUp(self): 

        self.url = [ 
            'users/create_user/', 
            'users/change_email/',
        ]
        self.User = get_user_model().objects.create_user(username='admin', email='testing@gmail.com', password='password123')



    def test_user_can_create_account(self): 

        data = { 
            'username': 'user11xx',
            'email': 'emailtest@gmail.com',
            'password': 'password123',
            'password2': 'password123'
        }
        request = self.client.post(self.url[0], data)
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)


    def test_user_can_change_email(self): 

        data = { 
            "email": "cattabaah@gmail.com", 
            "email2": "cattabaah@gmail.com"
        }
        request = self.client.post(self.url[1], data)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

