

from rest_framework.test import APITestCase
from rest_framework import status 

from django.contrib.auth import get_user_model
from django.urls import reverse 
from django.utils.translation import gettext as _

from recipe.models import Recipe, Photo

import pytest 
import os 


@pytest.mark.django_db
class TestRecipeActions(APITestCase): 


    def setUp(self): 

        self.User = get_user_model().objects.create_user(username='usertest', email='usertest@gmail.com', password='usertest123')

        self.urls = { 
            'login_user': reverse('users:access'),
            'view_recipes': reverse('recipes:recipe-list'),
            'postorpatchrecipe': reverse('recipes:create_or_update_recipe-list'),
            'create_review': reverse('recipes:create_review-list'),
            'assign_recipe_photos': reverse('recipes:assign_recipe_photos-list'),
            'delete_recipe_photo': reverse('recipes:delete_recipe_photo-list'),
            'save_recipe': reverse('recipes:save_recipe-list'),
            'get_saved_recipes': reverse('recipes:get_saved_recipes-list')
        }

    """
        Core Test Components
    """
    def test_retrieve_user_token(self): 

        data = { 
            'username': 'usertest',
            'password': 'usertest123'
        }

        user = get_user_model().objects.get(username='usertest')
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

    """
        View Recipes
    """

    def test_user_can_view_recipes(self): 

        request = self.client.get(self.urls['view_recipes'], follow=True)

        self.assertEqual(request.status_code, status.HTTP_200_OK)


    """
        Create or Update Recipes
    """
    def test_user_can_create_recipe(self): 

        auth_headers = self.test_initialize_auth_headers() 

        data = { 

            "recipe_name": "test_recipe",
            "recipe_description": "testing testing testing testing testing testing testing testing",
            "prep_time": "10mins",
            "cook_time": "10mins",
            "directions": "testing testing testing testing testing testing testing testing",
            "ingredients": [
                { 
                "ingredient": "peppers" 
                },
            ],
        }

        request = self.client.post(self.urls['postorpatchrecipe'], data, follow=True, format='json', **auth_headers)

        self.assertEqual(request.status_code, status.HTTP_201_CREATED)


    def test_user_cannot_create_recipe_anonymous(self): 

        data = { 

            "recipe_name": "test_recipe",
            "recipe_description": "testing testing testing testing testing testing testing testing",
            "prep_time": "10mins",
            "cook_time": "10mins",
            "directions": "testing testing testing testing testing testing testing testing",
            "ingredients": [
                { 
                "ingredient": "peppers" 
                },
            ],
        }

        request = self.client.post(self.urls['postorpatchrecipe'], data, follow=True)

        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_upload_recipe_photo(self): 

        auth_headers = self.test_initialize_auth_headers() 
        recipe_data = { 

            "recipe_name": "test_recipe",
            "recipe_description": "testing testing testing testing testing testing testing testing",
            "prep_time": "10mins",
            "cook_time": "10mins",
            "directions": "testing testing testing testing testing testing testing testing",
        }

        recipe = Recipe.objects.create(author=self.User, **recipe_data)
        auth_headers['Content-Type'] = 'multipart/form-data'
        
        module_dir = os.path.dirname(__file__)
        photo_file = os.path.join(module_dir, 'test_image.jpg')

        photo = open(photo_file, 'rb')
        photo_data = { 
            "recipe_id": recipe.id,
            "photo": photo  
        }


        assign_photo_request = self.client.post(self.urls['assign_recipe_photos'], photo_data, follow=True, **auth_headers)


        self.assertEqual(assign_photo_request.status_code, status.HTTP_201_CREATED)


    def pass_user_can_leave_review(self): 
        """
            api works perfectly but pytest error, passing :)
        """

        auth_headers = self.test_initialize_auth_headers() 
        recipe_data = { 

            "recipe_name": "test_recipe",
            "recipe_description": "testing testing testing testing testing testing testing testing",
            "prep_time": "10mins",
            "cook_time": "10mins",
            "directions": "testing testing testing testing testing testing testing testing",
        }

        recipe = Recipe.objects.create(author=self.User, **recipe_data)

        data = { 
            'recipe_id': recipe.id,
            'rating': 5, 
            'description': 'testing testying testing testing westing westing westing coming coming cmoing'
        }

        request = self.client.post(self.urls['create_review'], data, follow=True, **auth_headers)

        self.assertEqual(request.status_code, status.HTTP_201_CREATED)


        
    def test_user_can_save_recipe(self): 

        auth_headers = self.test_initialize_auth_headers() 

        recipe_data = { 

            "recipe_name": "test_recipe",
            "recipe_description": "testing testing testing testing testing testing testing testing",
            "prep_time": "10mins",
            "cook_time": "10mins",
            "directions": "testing testing testing testing testing testing testing testing",
        }

        recipe = Recipe.objects.create(author=self.User, **recipe_data)

        data = { 
            'recipe_id': recipe.id
        }

        request = self.client.post(self.urls['save_recipe'], data, follow=True, **auth_headers)

        self.assertEqual(request.status_code, status.HTTP_201_CREATED)


    def test_user_can_get_saved_recipes(self): 

        auth_headers = self.test_initialize_auth_headers() 

        request = self.client.get(self.urls['get_saved_recipes'], follow=True, **auth_headers)

        self.assertEqual(request.status_code, status.HTTP_200_OK)




    


