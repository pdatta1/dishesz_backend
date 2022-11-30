
from django.db import models
from django.utils import timezone 

from users.models import DisheszUser
from recipe.utils import photo_path

REVIEW_CHOICES = ( 
    (1,'HEAVILY DISLIKED'), 
    (1,'DISLIKED'), 
    (3,'FAIR'), 
    (4,'LIKE'), 
    (5, 'LOVED'),
)

RECIPE_CATEGORIES = ( 
    (1, 'Vegan'),
    (2, 'Spanish/Latin'),
    (3, 'Greek'), 
    (4, 'American'), 
    (5, 'Korean'), 
    (6, 'Japanese'),
    (7, 'Chinese'),
    (8, 'Italian'), 
    (8, 'Desserts'), 
    (9, 'Smoothie'),
)


class Recipe(models.Model): 

    recipe_name = models.CharField(max_length=24, blank=False, null=False)
    recipe_description = models.CharField(max_length=512, blank=False, null=False)
    prep_time = models.CharField(max_length=16, blank=False, null=False)
    cook_time = models.CharField(max_length=16, blank=False, null=False)
    directions = models.CharField(max_length=512, blank=False, null=False)
    created_on = models.DateTimeField(auto_now_add=timezone.now())

    category = models.CharField(max_length=16, choices=RECIPE_CATEGORIES, null=False, default=RECIPE_CATEGORIES[0][0])

    author = models.ForeignKey(to=DisheszUser, on_delete=models.CASCADE, related_name='user_recipes')

    

class Ingredient(models.Model): 

    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.CharField(max_length=32, blank=False, null=False)


class Photo(models.Model): 

    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to=f'uploads/{photo_path}')


class Review(models.Model): 

    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE, related_name='recipe_reviews')
    rating = models.IntegerField(choices=REVIEW_CHOICES, default=REVIEW_CHOICES[2])
    description = models.CharField(max_length=125, null=False, blank=False)
    author = models.ForeignKey(to=DisheszUser, on_delete=models.CASCADE, related_name='review_author')


class SavedRecipes(models.Model): 

    user = models.ForeignKey(to='users.DisheszUser', on_delete=models.CASCADE)
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE, related_name='saved_recipes', null=True)


