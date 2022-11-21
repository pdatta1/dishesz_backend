

from rest_framework import serializers 
from rest_framework.serializers import ModelSerializer


from recipe.models import (
    Recipe, 
    Ingredient, 
    Photo, 
    Review,
    SavedRecipes
)

class PhotoSerializer(ModelSerializer): 

    recipe = serializers.ReadOnlyField(source='recipe.recipe_name')
    photo = serializers.ImageField()


    class Meta: 
        model = Photo
        fields = ('photo', 'recipe' )





class IngredientSerializers(ModelSerializer): 

    recipe = serializers.ReadOnlyField(source='recipe.recipe_name')
    ingredient = serializers.CharField(max_length=32, allow_blank=False, required=True)

    class Meta: 
        model = Ingredient
        fields = ('recipe', 'ingredient', )

class ReviewSerializer(ModelSerializer): 

    recipe = serializers.ReadOnlyField(source='recipe.recipe_name')
    rating = serializers.IntegerField()
    description = serializers.CharField(style={'base_template': 'textarea.html'}, max_length=125, allow_blank=False)
    
    author = serializers.ReadOnlyField(source='author.username')


    class Meta: 
        model = Review
        fields = ('recipe', 'rating', 'description', 'author', )

class SavedRecipesSerializer(ModelSerializer): 

    user = serializers.ReadOnlyField(source='user.username')

    class Meta: 
        model = SavedRecipes
        fields = ('user', )

class RecipeSerializer(ModelSerializer): 

    recipe_name = serializers.CharField(min_length=4, max_length=24, allow_blank=False, required=True)
    recipe_description = serializers.CharField(style={'base_template': 'textarea.html'}, min_length=24, max_length=512, allow_blank=False, required=True)
    prep_time = serializers.CharField(max_length=24, allow_blank=False, required=True)
    cook_time = serializers.CharField(max_length=24, allow_blank=False, required=True)
    directions = serializers.CharField(min_length=24, max_length=512, allow_blank=False, required=True)

    ingredients = IngredientSerializers(many=True)
    photos = PhotoSerializer(many=True)
    recipe_reviews = ReviewSerializer(read_only=True, many=True)
    saved_recipes = SavedRecipesSerializer(many=True)

    author = serializers.ReadOnlyField(source='author.username')
    created_on = serializers.ReadOnlyField() 


    def create(self, validated_data): 

        # pop request data
        recipe_data = validated_data.pop('recipe')
        ingredient_data = validated_data.pop('ingredients')

        # create recipe
        recipe = Recipe.objects.create(**recipe_data)

        # assign nested data 
        for data in ingredient_data: 
            ingredients = Ingredient.objects.create(recipe=recipe, **data)
            ingredients.save() 
        
        recipe.save() 
        return recipe 
        
    class Meta: 
        model = Recipe
        fields = ('id', 'recipe_name', 'recipe_description', 'prep_time', 'cook_time', 'directions', 'photos', 'ingredients', 'recipe_reviews', 'author','created_on', 'saved_recipes')




