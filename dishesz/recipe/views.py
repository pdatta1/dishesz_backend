

from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet, ModelViewSet, GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status 
from rest_framework import parsers 


from recipe.models import  Recipe, Photo, Review, SavedRecipes 
from recipe.serializers import  PhotoSerializer, RecipeSerializer
from recipe.pagination import RecipeViewPagination

from users.permissions import IsOwner

from notify.core.send_notify import handle_saves_notification


class ViewRecipeViewSet(ReadOnlyModelViewSet): 
    """
         Displays all recipes data
         This class is a readonly api view 
    """
    queryset = Recipe.objects.all() 
    serializer_class = RecipeSerializer
    permission_classes = (AllowAny, )
    pagination_class = RecipeViewPagination




                         
class RecipeModelViewSet(ModelViewSet):

    """
        Allows Authenticated Users to create their recipe
    """

    permission_classes = (IsAuthenticated, )
    queryset = Recipe.objects.all() 
    serializer_class = RecipeSerializer
    http_method_names = ['post', 'patch']

    def perform_create(self, serializer): 
        """
            Create Recipe by Requested Authenticated user
            :param serializer: given serializer to be saved
        """
        serializer.save(author=self.request.user)
    



class AssignPhotoToRecipeAPI(ModelViewSet): 
    """
        This class is responsible for uploading photos and 
        assign them to the correlating recipe model object
    """

    permission_classes = (AllowAny, )
    parser_classes = (parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser)
    queryset = Photo.objects.all() 
    serializer_class = PhotoSerializer

    def perform_create(self, serializer): 
        """
            Create and Assign photo to existing recipe model
            :param serializer: Given Serializer to be saved
        """

        recipe = Recipe.objects.get(id=self.request.data['recipe_id'])
        serializer.save(recipe=recipe)


class DeletePhotoAssignAPI(ViewSet): 

    """
        Allows Authenticated User to Delete existing photo 
    """

    permission_classes = (IsOwner, )

    def delete_photo(self, photo_id): 
        """
            Fetch existing photos and delete 
            :param photo_id: given id of the photo within the Photo Model
        """
        photo = Photo.objects.get(id=photo_id)
        photo.delete() 

    def create(self, request): 

        """
            api create view 
        """
        data = request.data 
        self.delete_photo(photo_id=data['photo_id'])

        return Response(status=status.HTTP_200_OK, data={
            'message': 'photo deleted'
        })





class LeaveReview(ViewSet): 

    """
        Allows user to leave a review on specific recipe
    """

    permission_classes = (IsAuthenticated, )


    def create_review(self, user, review_data): 
        """
            :param user: requested user to assign/attach review 
            :param review_data: data of the review
        """
        
        # retrieve recipe id from review_data(dict) and get recipe by id
        recipe_id = review_data['recipe_id']
        recipe = Recipe.objects.get(id=recipe_id)


        # create review and return review
        review = Review.objects.create(author=user, recipe=recipe, **review_data)
        return ( recipe, review )

    def create(self, request): 

        data = request.data 
        auth_user = request.user 

        recipe_data, review_data = self.create_review(auth_user, data)
        handle_saves_notification(request.user.username, recipe_data.author.username, recipe_data.id)

        return Response(status=status.HTTP_201_CREATED, data={ 
            'message': f'Review Created on Recipe {review_data.recipe}',
            'notify': recipe_data.author.username 
        })
    


class SavedRecipe(ViewSet): 
    """
        SavedRecipe API ViewSet: 
            :purpose:   enable user to save a specific recipe 
                        of his/hers choosing
                    
    """

    permission_classes = (IsAuthenticated, )

    def save_recipe(self, user, recipe_id): 
        """
            allows user to save recipe by creating a savedrecipes model attached to requested user
            :param user: requested user used to attached model
            :param recipe_id: recipe id that the user choose to save

        """

        # retrieve recipe
        recipe = Recipe.objects.get(id=recipe_id)

        #create and save recipes 
        _create_save_recipe = SavedRecipes.objects.create(user=user, recipe=recipe)
        _create_save_recipe.save() 

    def unsaved_recipe(self, user, recipe_id): 

        recipe = Recipe.objects.get(id=recipe_id)
        unsaved_recipe = SavedRecipes.objects.get(user=user, recipe=recipe)
        unsaved_recipe.delete() 

    def create(self, request): 
        data = request.data 

        if data['action'] == 'saving':
            self.save_recipe(request.user, data['recipe_id'])
            return Response(status=status.HTTP_201_CREATED, data={
                'message': 'recipe saved'
            })

        if data['action'] == 'unsaving': 
            self.unsaved_recipe(request.user, data['recipe_id']) 
            return Response(status=status.HTTP_200_OK, data={ 
                'message': 'recipe unsaved'
            })
        


class MySavedRecipesAPI(ViewSet): 

    permission_classes = (IsOwner, )

    def get_saved_recipes(self, user): 
        try: 
            recipes = Recipe.objects.filter(saved_recipes__user=user)
            return recipes 

        except Recipe.DoesNotExist: 
            return None 

    def list(self, request): 

        recipes = self.get_saved_recipes(request.user)
        serialized_data = RecipeSerializer(recipes, many=True)
        
        return Response(status=status.HTTP_200_OK, data=serialized_data.data)

        
        
        

class InterestLookupAPI(GenericViewSet): 

    """
        Lookup All Recipes Based on searched interest
    """

    permission_classes = ( AllowAny, )

    def get_recipes_by_interest(self, interest_name): 

        recipes = Recipe.objects.filter(category=interest_name)
        return recipes 

    def serialize_recipes(self, page): 

        serializer = RecipeSerializer(page, many=True)
        return serializer.data 

    def paginate_recipes(self, recipes): 

        page = self.paginate_queryset(recipes)
        if page is not None: 
            serializer = self.serialize_recipes(page)
            return self.get_paginated_response(serializer)

        serializer = self.serialize_recipes(recipes)
        return serializer 




    def list(self, request): 

        interest_name = request.query_params.get('interest_name')
        
        recipes = self.get_recipes_by_interest(interest_name)
        page = self.paginate_recipes(recipes)

        return Response(status=status.HTTP_200_OK, data={ 
            'recipes': page 
        })



class AllRecipeCategoriesAPI(ViewSet): 

    def get_all_categories(self): 

        data = [] 
        categories = Recipe.objects.values('category')
        
        for category in categories: 
            data.append(category['category'])

        return set(data)


    def list(self, request): 
        
        all_categories = self.get_all_categories() 

        return Response(status=status.HTTP_200_OK, data=all_categories)
    
