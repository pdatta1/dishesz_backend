
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework import filters 
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated

from rest_framework.generics import ListAPIView

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from users.views import display_generic_green_status, display_generic_red_status
from users.models import ( 
    InterestContainer, 
    Interest, 
    DisheszUserFollowing
)
from users.views import LookupUserProfileEssentials, get_user 

from recipe.models import Recipe 
from recipe.serializers import RecipeSerializer
from recipe.pagination import RecipeViewPagination




class EstablishUserInterestAPI(ViewSet): 
    """
        This class is responsible for setting up user 
        interests that will be later used to general a feed

        @methods: 
            - create_container -> creates the user interest container model
            - add_interest -> create an interest model for requested_user
            - add_multiple_interests -> add an array of user interests dict to model
    """

    permission_classes = (IsAuthenticated, )

    def create_or_get_container(self, requested_user): 

        container = None 
        if InterestContainer.objects.filter(dishesz_user=requested_user).exists(): 
            container = InterestContainer.objects.get(dishesz_user=requested_user)
            return container 
            

        container = InterestContainer.objects.create(dishesz_user=requested_user)
        return container 

    
    def add_interest(self, container, data): 

        if not self.check_duplicate_interest(container, data['interest_name']):
            interest = Interest.objects.create(container=container, **data)
            interest.save()
            return interest
         

    def check_duplicate_interest(self, container, interest_name): 

        duplicate_interest_name = Interest.objects.filter(container=container, interest_name=interest_name)
        if duplicate_interest_name.exists(): 
            return True 
        return False 

    def add_multiple_interest(self, container, interest_list):

        # array to return 
        response_data = [] 

        # loop thru interest list 

        for data in interest_list: 

            # check for duplicates ( if duplicates -> ignore, else -> create interest)
            if not self.check_duplicate_interest(container, data['interest_name']): 
                interest = Interest.objects.create(container=container, **data)
                interest.save() 
                response_data.append(interest.interest_name)

        return response_data 


    def create(self, request): 

        # retrieve and initialize requested data(s)
        requested_data = request.data 
        requested_user = request.user 

        #print(f'requested data {requested_data}')

        # create container or get the container 
        user_container = self.create_or_get_container(requested_user=requested_user)

        if type(requested_data) == dict: 
            interest = self.add_interest(container=user_container, data=requested_data)
            if interest:
                _dict, _status = display_generic_green_status(f'interest added {interest.interest_name}')
                return Response(status=_status, data=_dict)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'error'})

        if type(requested_data) == list: 
            print('running the list')
            interest = self.add_multiple_interest(container=user_container, interest_list=requested_data)
            _dict, _status = display_generic_green_status(f'interests added {interest}')
            return Response(status=_status, data=_dict)


        _dict, _status = display_generic_red_status(f'Error Adding Interests')
        return Response(status=_status, data=_dict)
                 

    


class GenerateUserFeeds(ViewSet): 
    """
        This class is responsible for generate user feeds based 
        on liked or saved interests and followings
    """

    permission_classes = (IsAuthenticated, ) 


    def get_user_container(self): 
        return InterestContainer.objects.get(dishesz_user=self.request.user)

    def get_user_interests(self, user_container): 
        return Interest.objects.filter(container=user_container)

    def get_recipe_by_interests(self, interests): 
        return Recipe.objects.filter(category__in=interests)

    def get_following_recipes(self): 
        
        # initialize array to host all followings user for filtering later
        followings_data = [] 

        # get followings objects
        followings = DisheszUserFollowing.objects.filter(dishesz_user=self.request.user)

        # append to followings_data 
        for user in followings: 
            followings_data.append(user.user_follow) 

        # filter recipe by users' following
        recipe = Recipe.objects.filter(author__in=followings_data).order_by('created_on')
        return recipe 



    def generate_interested_recipes(self): 

        # initialize interest data array 
        interests_data = [] 

        # get the container and interests belong to such container
        container = self.get_user_container()
        interests = self.get_user_interests(user_container=container)

        # traversal the interests and append each interest_name to interests_data
        for interest in interests: 
            interests_data.append(interest.interest_name)

        # filter recipe with categories filter by interests_data elements
        recipes = Recipe.objects.filter(category__in=interests_data).order_by('created_on')

        # return recipes 
        return recipes 


    def list(self, request): 


        user_feeds = []  

        recipe_feeds = self.generate_interested_recipes() 
        followings_feed = self.get_following_recipes() 

        recipe_serializer = RecipeSerializer(recipe_feeds, many=True)
        followings_serializer = RecipeSerializer(followings_feed, many=True)

        user_feeds = recipe_serializer.data + followings_serializer.data 


        return Response(status=status.HTTP_200_OK, data={
            'feeds': user_feeds
        })


class GenericLookupAPI(GenericViewSet): 

    """"
        This API is responsible for lookup of anything such as recipes, users, etc.
    """

    
    def get_recipe(self, recipe_name): 

        if Recipe.objects.filter(recipe_name=recipe_name).exists(): 
            recipe = Recipe.objects.get(recipe_name=recipe_name)
            serializer = RecipeSerializer(recipe, many=False)
            return serializer.data 
        return None 

    
    def get_user(self, username): 

        essentials = LookupUserProfileEssentials() 

        if get_user_model().objects.filter(username=username).exists(): 

            user = get_user_model().objects.get(username=username)
            essentials.serialized_response_data(user)
            return essentials.get_serialized_data()

        return None 

    
    def list(self, request): 


        search_query = request.query_params.get('search_query')

        searched_recipe = self.get_recipe(search_query)
        search_user = self.get_user(search_query)

        if searched_recipe is not None: 
            return Response(status=status.HTTP_200_OK, data={ 
                'recipe': searched_recipe
            })

        if search_user is not None: 
            return Response(status=status.HTTP_200_OK, data={ 
                'user': search_user
            })

        return Response(status=status.HTTP_200_OK, data=None)        

            


        

    
    

    

            

