from django.urls import path, include 

from rest_framework.routers import DefaultRouter

from recipe.views import ( 
    AssignPhotoToRecipeAPI, 
    DeletePhotoAssignAPI, 
    MySavedRecipesAPI, 
    RecipeModelViewSet, 
    LeaveReview, 
    SavedRecipe, 
    ViewRecipeViewSet,
    InterestLookupAPI
)


recipe_router = DefaultRouter()
recipe_router.register(r'view_recipes', ViewRecipeViewSet, basename='recipe')
recipe_router.register(r'create_or_update_recipe', RecipeModelViewSet, basename='create_or_update_recipe')
recipe_router.register(r'create_review', LeaveReview, basename='create_review')
recipe_router.register(r'assign_recipe_photos', AssignPhotoToRecipeAPI, basename='assign_recipe_photos')
recipe_router.register(r'delete_recipe_photo', DeletePhotoAssignAPI, basename='delete_recipe_photo')
recipe_router.register(r'save_recipe', SavedRecipe, basename='save_recipe')
recipe_router.register(r'get_saved_recipes', MySavedRecipesAPI, basename='get_saved_recipes')
recipe_router.register(r'interest_lookup', InterestLookupAPI, basename='interest_lookup')

app_name = 'recipes'
urlpatterns = [ 
    path('', include(recipe_router.urls)),
]