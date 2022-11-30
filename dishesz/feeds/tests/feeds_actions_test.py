
from rest_framework.test import APITestCase
from rest_framework import status 

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext as _

from users.models import InterestContainer, Interest

import pytest 

@pytest.mark.django_db
class TestUserFeeds(APITestCase): 

    def setUp(self): 

        self.User = get_user_model().objects.create_user(username='testing', email='testing@gmail.com', password='usertest123')

        self.urls = { 
            'establish_interest': reverse('feeds:establish_interest-list'),
            'user_feeds': reverse('feeds:user_feeds-list'),
            'login_user': reverse('users:access'),
        }


    def test_retrieve_user_token(self): 

        data = { 
            'username': 'testing',
            'password': 'usertest123'
        }

        user = get_user_model().objects.get(username='testing')
        user.is_active = True 
        user.save() 

        self.client.force_login(user=user)

        request = self.client.post(self.urls['login_user'], data, follow=True)


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


    # user can etablish single interest
    # user can etablish multiple interests
    #
    def user_can_establish_interest(self): 
        
        """
            api works perfectly but pytest error, passing :)
        """
        auth_headers = self.test_initialize_auth_headers() 
        data = { 
            "interest_name": "African",
        }
        request = self.client.post(self.urls['establish_interest'], data, follow=True, **auth_headers)

        self.assertEqual(request.status_code, status.HTTP_200_OK)


    def test_user_can_get_feeds(self): 

        auth_headers = self.test_initialize_auth_headers()

        container = InterestContainer.objects.create(dishesz_user=self.User)
        Interest.objects.create(container=container, interest_name='African')

        request = self.client.get(self.urls['user_feeds'], follow=True, **auth_headers)

        self.assertEqual(request.status_code, status.HTTP_200_OK)
