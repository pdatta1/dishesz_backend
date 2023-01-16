

from rest_framework import serializers 
from rest_framework.serializers import ModelSerializer


from recipe.models import (
    Recipe, 
    Ingredient, 
    IngredientAvailableAt,
    Photo, 
    Review,
    SavedRecipes
)

class PhotoSerializer(ModelSerializer): 

    recipe = serializers.ReadOnlyField(source='recipe.recipe_name')
    src = serializers.ImageField()


    class Meta: 
        model = Photo
        fields = ('src', 'recipe' )


class IngredientAvailableAtSerializer(ModelSerializer): 

    ingredient = serializers.ReadOnlyField(source='ingredient.ingredient')
    store_name = serializers.CharField(max_length=24, allow_blank=False)
    store_price = serializers.DecimalField(max_digits=5, decimal_places=2, default=None)
    store_link = serializers.URLField(max_length=300, allow_blank=True, required=False)


    class Meta: 
        model = IngredientAvailableAt
        fields = ('ingredient', 'store_name', 'store_price', 'store_link')


class IngredientSerializers(ModelSerializer): 

    recipe = serializers.ReadOnlyField(source='recipe.recipe_name')
    ingredient = serializers.CharField(max_length=32, allow_blank=False, required=True)
    available_at = IngredientAvailableAtSerializer(many=True)

    class Meta: 
        model = Ingredient
        fields = ('recipe', 'ingredient', 'available_at', )


class ReviewSerializer(ModelSerializer): 

    recipe = serializers.ReadOnlyField(source='recipe.recipe_name')
    rating = serializers.IntegerField()
    description = serializers.CharField(style={'base_template': 'textarea.html'}, max_length=125, allow_blank=False)
    
    author = serializers.ReadOnlyField(source='author.username')
    profile_pic = serializers.ReadOnlyField(source='author.user_profile.get_profile_pic_src')


    class Meta: 
        model = Review
        fields = ('recipe', 'rating', 'description', 'author', 'profile_pic', )

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
    category = serializers.CharField(max_length=65, allow_blank=False)

    ingredients = IngredientSerializers(many=True)
    photos = PhotoSerializer(read_only=True, many=True)
    recipe_reviews = ReviewSerializer(read_only=True, many=True)
    saved_recipes = SavedRecipesSerializer(read_only=True, many=True)

    author = serializers.ReadOnlyField(source='author.username')
    profile_pic = serializers.ReadOnlyField(source='author.user_profile.get_profile_pic_src')
    created_on = serializers.ReadOnlyField() 


    def create(self, validated_data): 

        # pop request data
        ingredient_data = validated_data.pop('ingredients')

        # create recipe
        recipe = Recipe.objects.create(**validated_data)

        # assign nested data 
        for data in ingredient_data: 

            # pop available at object 
            available_at = data.pop('available_at')

            # create ingredient model 
            ingredients = Ingredient.objects.create(recipe=recipe, **data)
            ingredients.save() 

            # loop thru available_at array and create available_at model for assigned ingredient
            for available_data in available_at: 
                available_model = IngredientAvailableAt.objects.create(ingredient=ingredients, **available_data)
                available_model.save()


        # finalize
        recipe.save() 
        return recipe 
        

    class Meta: 
        model = Recipe
        fields = ('id', 'recipe_name', 'recipe_description', 
                    'prep_time', 'cook_time', 'directions', 'photos', 
                        'ingredients', 'recipe_reviews', 'author','created_on', 
                            'saved_recipes', 'category', 'profile_pic',)



