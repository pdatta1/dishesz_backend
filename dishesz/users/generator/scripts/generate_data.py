

import os 
import json 
import random
import requests 

from urllib import request

from django.core.files import File 

from users.models import ( 
    DisheszUser, 
    DisheszUserFollowing, 
    DisheszUserFollowers,
    InterestContainer,
    Interest,
)
from recipe.models import ( 
    Recipe, 
    Ingredient, 
    IngredientAvailableAt, 
    Photo, 
    Review, 
    SavedRecipes,
)
from users.generator.scripts.interests import interests
import users as dishesz_user

from progress.bar import Bar 

class GenerateData(object):
    """
        @purpose: generate fake data for development on the user model 
    """

    def __init__(self, clean_database=False): 

        """
            :param file_directory: path of json file to pull users data
            :module_dir: get the base directory of users app 
            :file_dir: join the base directory of users app
            :progress: counter to display while generating user model
        """

        self.module_dir = os.path.dirname(dishesz_user.__file__)
        self.photo_array = [ 
            "https://static01.nyt.com/images/2022/10/11/dining/kc-manicotti-copy/kc-manicotti-mediumSquareAt3X.jpg",
            "https://a.cdn-hotels.com/gdcs/production0/d1513/35c1c89e-408c-4449-9abe-f109068f40c0.jpg?impolicy=fcrop&w=800&h=533&q=medium",
            "https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/copycat-hamburger-helper1-1659463591.jpg?crop=0.668xw:1.00xh;0.176xw,0&resize=640:*",
            "https://www.tasteofhome.com/wp-content/uploads/2022/03/GettyImages-1178684940-scaled-e1647271049457.jpg",
            "https://www.westcentralfoodservice.com/wp-content/uploads/2019/04/5-food-trends-2019-no-title.jpg",
        ]

        if clean_database:
            self.cleanup_user_model() 

    def change_module_dir(self, new_module_dir): 
        self.module_dir = os.path.dirname(new_module_dir.__file__)

    def create_file_module(self, file_directory): 
        """
            @purpose: convert strings into path
            @param file_directory: 
        """
        return os.path.join(self.module_dir, file_directory)

    def generate_fake_users(self, file_directory): 

        """
            @purpose: 
                open the file directory,
                read the data from file, 
                convert to list[dicts]

                iterate the converted list[dicts]
                create user model on each dict of converted list[dicts]
                set user is_active to True 
                save && increment the progress
        """
        file_module = self.create_file_module(file_directory)

        with open(file_module, 'r') as user_file: 

            data = user_file.read() 
            users_dict = json.loads(data)
            progress = Bar('Generating Users Data', max=len(users_dict))

            for user in users_dict: 

                

                user = DisheszUser.objects.create_user(**user)
                user.is_active = True 
                user.save() 
                
                progress.next() 

            progress.finish() 


    def generate_recipes(self, file_directory): 
        """
            @purpose: 
                generate recipes form json for recipe model 
        """

        file_module = self.create_file_module(file_directory)

        with open(file_module, 'r') as recipe_file: 

            data = recipe_file.read() 
            recipe_dict = json.loads(data)
            progress = Bar('Generating Recipes Data', max=len(recipe_dict))

            for recipe in recipe_dict: 

                random_id = random.choice(list(self.get_all_users_ids()))
                user = DisheszUser.objects.get(id=random_id)

                Recipe.objects.create(author=user, **recipe)

                progress.next() 
            progress.finish() 

    def generate_ingredients(self, file_directory): 
        """
            @purpose: 
                generate ingredient data for ingredient model from json file
        """

        file_module = self.create_file_module(file_directory)

        with open(file_module, 'r') as ing_file: 

            data = ing_file.read() 
            ingredients = json.loads(data)
            progress = Bar('Generating Ingredient Data', max=len(ingredients))

            for ingredient in ingredients: 

                random_id = random.choice(list(self.get_all_recipes_ids()))
                recipe = Recipe.objects.get(id=random_id)

                Ingredient.objects.create(recipe=recipe, **ingredient)

                progress.next() 
            progress.finish() 

    def generate_reviews(self, file_directory): 
        
        file_module = os.path.join(self.module_dir, file_directory)

        with open(file_module, 'r') as review_file: 

            data = review_file.read() 
            reviews = json.loads(data)
            progress = Bar('Generating Review Data', max=len(reviews))


            for review in reviews: 

                user_id = random.choice(list(self.get_all_users_ids()))
                recipe_id = random.choice(list(self.get_all_recipes_ids()))

                reviewer = DisheszUser.objects.get(id=user_id)
                recipe = Recipe.objects.get(id=recipe_id)

                Review.objects.create(recipe=recipe, author=reviewer, **review)

                progress.next()
            progress.finish()

    def generate_saved_recipes(self): 

        recipes = list(self.get_all_recipes())
        users = DisheszUser.objects.all() 

        max_saved = 50
        progress = Bar('Generating Saved Recipes', max=len(recipes))

        for user in users:

            sample_saved_recipes = random.sample(recipes, max_saved)

            for saved in sample_saved_recipes: 

                SavedRecipes.objects.create(user=user, recipe=saved)

            progress.next() 

        progress.finish() 

                







    def generate_stores(self, file_directory): 
        """
            @purpose: 
                generate store data for store model from json file
        """
        file_module = self.create_file_module(file_directory)

        with open(file_module, 'r') as store_file: 

            data = store_file.read() 
            stores = json.loads(data)

            progress = Bar('Generating Stores Data', max=len(stores))

            for store in stores: 
                random_id = random.choice(list(self.get_all_ingredients_ids()))
                random_price = random.uniform(1.5, 100.5)

                store['store_price'] = random_price

                ingredient = Ingredient.objects.get(id=random_id)
                IngredientAvailableAt.objects.create(ingredient=ingredient, **store)

                progress.next() 
            progress.finish() 

    def get_photo_files(self): 
        
        for photo in self.photo_array: 
            downloader = request.urlopen(photo)
            yield downloader


    def send_data(self, url, data): 

        request = requests.post(url, data, { 
            'Content-Type': 'multipart/form-data'
        })

        return request.status_code


    def generate_photos(self): 
        """
            @purpose: 
                generate photos data for photo model form json file
        """

        progress = Bar("Generating Photo Data", max=len(self.photo_array))

        id_saved = []


        for photo in self.photo_array: 

            random_id = random.choice(list(self.get_all_recipes_ids()))
            recipe = Recipe.objects.get(id=random_id)

            Photo.objects.create(recipe=recipe, src=photo)

            id_saved.append(recipe.id)
            progress.next() 
        progress.finish() 

        print(f'Ids Saved {id_saved}')


    def add_user_interests(self): 
        
        categories = interests() 
        max_interest = 5
        progress = Bar("Generating User Interests", max=len(categories))
        model_users = DisheszUser.objects.all() 

        for user in model_users: 
                
                container = InterestContainer.objects.get(dishesz_user=user)
                sampled_interests = random.sample(categories, max_interest)

                for interest in sampled_interests: 
                    Interest.objects.create(container=container, interest_name=interest)
                
                progress.next() 
        progress.finish() 

    def randomize_follow(self): 
        """
            @purpose: 
                randomize follow users
        """
        follow_count = len(list(self.get_all_users_ids()))
        progress = Bar('Generate Follow Data', max=follow_count)

        for follow_request in range(1, follow_count):

            initial_id = random.choice(list(self.get_all_users_ids()))
            follow_id = random.choice(list(self.get_all_users_ids()))

            initial_user = DisheszUser.objects.get(id=initial_id)
            follow_user = DisheszUser.objects.get(id=follow_id)

            DisheszUserFollowing.objects.create(dishesz_user=initial_user, user_follow=follow_user)
            DisheszUserFollowers.objects.create(dishesz_user=follow_user, follower=initial_user)

            progress.next() 
        progress.finish() 

     


    def cleanup_user_model(self): 
        """
            @purpose: 
                clean user model by deleting all models
        """
        users = DisheszUser.objects.all() 
        progress = Bar("Cleaning up Database", max=len(users))
        for user in users: 
            if user.username != 'usertest': 
                user.delete() 
                progress.next()
        progress.finish() 
        
        Recipe.objects.all().delete() 
        Ingredient.objects.all().delete() 
        IngredientAvailableAt.objects.all().delete() 
        Photo.objects.all().delete() 
        DisheszUserFollowers.objects.all().delete()
        DisheszUserFollowing.objects.all().delete() 
        SavedRecipes.objects.all().delete() 
        Interest.objects.all().delete() 


    def get_all_users_ids(self): 

        """
            @purpose: get all users ids data model
        """

        users = DisheszUser.objects.all() 
        for user in users: 
            yield user.id 


    def get_all_recipes_ids(self): 
        """
            @purpose: get all recipes ids from user model 
        """
        
        recipes = Recipe.objects.all() 
        for recipe in recipes: 
            yield recipe.id 

    def get_all_ingredients_ids(self): 
        """
            @purpose: get all ingredients ids from ingredient model
        """

        ingredients = Ingredient.objects.all() 
        for ingredient in ingredients: 
            yield ingredient.id

    
    def get_all_recipes(self): 

        recipes = Recipe.objects.all() 
        for recipe in recipes: 
            yield recipe 




    


