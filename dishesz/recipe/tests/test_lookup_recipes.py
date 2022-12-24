

from rest_framework.test import APITestCase
from rest_framework import status 

from django.urls import reverse 

from recipe.models import Recipe
import recipe

from users.generator.scripts.generate_data import GenerateData

import pytest 
import random 




@pytest.mark.django_db
class RecipeLookupTest(APITestCase): 


    def setUp(self): 
        
        self.urls = {
            'interest_lookup': reverse('recipes:interest_lookup-list'),
        }

        self.generator = GenerateData(clean_database=False) 
        self.generator.change_module_dir(recipe)
        self.generator.generate_recipes('tests/json/recipes.json')



    def get_all_recipes_categories(self): 

        recipes = Recipe.objects.all() 

        for recipe in recipes: 
            yield recipe.category 


    def test_user_can_lookup_recipe_by_interest(self): 

        category = random.choice(list(self.get_all_recipes_categories()))
        search_url = f"self.urls['interest_lookup']/?interest_name={category}"

        response = self.client.get(search_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        



