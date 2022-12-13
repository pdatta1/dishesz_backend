
import os 
import json

import random 

from users.models import DisheszUser
from recipe.models import Recipe, Ingredient, IngredientAvailableAt, Photo 
from recipe.serializers import PhotoSerializer
import users as dishesz_user

import requests 

from decouple import config 


def get_user_token(): 

    data = { 
        'username': 'usertest',
        'password': 'usertest123',
    }

    token = requests.post('https://scrapnc.com/users/access/', data, { 
         'Content-Type': 'application/json'
    })

    if token.status_code == 200:

        response_data = json.loads(token.text)
        return response_data['access']

    return token.status_code


def cleanup_database(): 

    Recipe.objects.all().delete() 
    Ingredient.objects.all().delete() 
    IngredientAvailableAt.objects.all().delete() 
    Photo.objects.all().delete() 

def generate_fake_users(): 

    module_dir = os.path.dirname(dishesz_user.__file__)
    file_dir = os.path.join(module_dir, 'generator/users.json')

    with open(file_dir, 'r') as user_file:

        data = user_file.read() 
        users = json.loads(data)
        for user in users: 
            created_user = DisheszUser.objects.create_user(**user)
            created_user.is_active = True 
            created_user.save()


def get_all_recipe_id(): 
     
    id_list = [] 
    recipes = Recipe.objects.all()
    for recipe in recipes: 
        id_list.append(recipe.id)

    return id_list

def get_all_users_id(): 
    id_list = [] 
    users = DisheszUser.objects.all() 
    for user in users: 
        id_list.append(user)

    return id_list

def get_all_ingredients_id(): 

    ids = [] 
    ingredients = Ingredient.objects.all() 
    for ing in ingredients: 
        ids.append(ing.id)

    return ids 

def populate_recipe_data(): 

    token = get_user_token() 

    module_dir = os.path.dirname(dishesz_user.__file__)
    recipe_dir = os.path.join(module_dir, 'generator/recipes.json')
    ingredient_dir = os.path.join(module_dir, 'generator/ingredients.json')
    store_dir = os.path.join(module_dir, 'generator/stores.json')
    
    progress = 0 

    print('Starting Recipe Data')

    with open(recipe_dir, 'r') as recipe_file: 

        data = recipe_file.read() 
        recipes = json.loads(data)

        for recipe in recipes: 
            random_id = random.choice(get_all_users_id)
            user = DisheszUser.objects.get(id=random_id)
            Recipe.objects.create(author=user, **recipe)
            progress += 1
            print(f'Progress at {progress}%')

    progress = 0 

    print('Starting Ingredient Data')

    with open(ingredient_dir, 'r') as ing_file: 

        data = ing_file.read() 
        ingredients = json.loads(data)

        for ingredient in ingredients: 
            random_id = random.choice(get_all_recipe_id())
            recipe = Recipe.objects.get(id=random_id)
            Ingredient.objects.create(recipe=recipe, **ingredient)
            progress += 1
            print(f'Progress at {progress}%')


    progress = 0 

    with open(store_dir, 'r') as store_file: 

        data = store_file.read() 
        stores = json.loads(data)

        for store in stores: 
            random_id = random.choice(get_all_ingredients_id())
            random_price = random.uniform(1.5, 100.5)
            ingredient = Ingredient.objects.get(id=random_id)
            IngredientAvailableAt.objects.create(ingredient=ingredient, 
                    store_name=store['store_name'], store_price=random_price, 
                    store_link=store['store_link'])
            progress += 1
            print(f'Progress at {progress}%')


    progress = 0 

    photos = [] 
    base_dir = os.path.join(module_dir, 'generator')
    for images in os.listdir(base_dir): 
        if (images.endswith(".jpg")): 
            photos.append(images)

    
    for photo in photos: 
            random_id = random.choice(get_all_recipe_id())
            recipe = Recipe.objects.get(id=random_id)
            p_dir = os.path.join(module_dir, f'generator/{photo}')
            photo_file = open(p_dir, 'rb')
            photo_data = { 
                'recipe': recipe.id,
                'src': photo_file
            }

            requests.post('https://scrapnc.com/recipe/assign_recipe_photos', photo_data, {
                'Content-Type': 'multipart/form-data',
                'Authorization': f'Bearer {token}'
            })
            progress += 1
            print(f'Progress at {progress}%')






def run_generator(): 

    print('Cleaning Database')
    cleanup_database() 
    populate_recipe_data()



   


 



run_generator()