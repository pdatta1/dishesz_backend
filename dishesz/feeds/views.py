
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework import filters 
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated

from rest_framework.generics import ListAPIView

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Q 

from users.views import display_generic_green_status, display_generic_red_status
from users.models import ( 
    InterestContainer, 
    Interest, 
    DisheszUserFollowing
)
from users.essentials import LookupUserProfileEssentials

from recipe.models import Recipe 
from recipe.serializers import RecipeSerializer
from recipe.pagination import RecipeViewPagination


from itertools import chain 



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
                 

    


class GenerateUserFeeds(GenericViewSet): 
    """
        This class is responsible for generate user feeds based 
        on liked or saved interests and followings
    """

    permission_classes = (IsAuthenticated, ) 
    serializer_class  = RecipeSerializer
    pagination_class = RecipeViewPagination
    


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

    
    def get_queryset(self):

        recipe_feeds = self.generate_interested_recipes() 
        following_feeds = self.get_following_recipes() 

        user_feeds = list(chain(recipe_feeds, following_feeds))
        return user_feeds


    def list(self, request, *args, **kwargs): 


        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None: 
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

        

class GenericLookupAPI(GenericViewSet): 

    """"
        This API is responsible for lookup of anything such as recipes, users, etc.
    """

    
    def get_recipes(self, recipe_name): 

        """
            Get Recipe by name if exists 
            :param recipe_name: recipe_name to be retrieved
            :returns None if recipe do not exist 
        """

        if Recipe.objects.filter(recipe_name__contains=recipe_name).exists(): 
            recipes = Recipe.objects.filter(recipe_name__contains=recipe_name)
            serializer = RecipeSerializer(recipes, many=True)
            return serializer.data 
        return None 

    
    def get_users(self, username): 

        """
            Get User by username if exists 
            :param username: username to be retrieve
            :returns None if recipe do not exist
        """

        essentials = LookupUserProfileEssentials() 

        if get_user_model().objects.filter(username=username).exists(): 

            user = get_user_model().objects.get(username=username)

            essentials.serialized_response_data(user)
            return essentials.get_serialized_data()

        return None 

    
    def list(self, request): 

        """
            get search_query param from request, get searched user or recipe, 
            and return api response 
        """

        users_query = [] 
        search_query = request.query_params.get('search_query')

        searched_recipes = self.get_recipes(search_query)
        search_users = self.get_users(search_query)

        if searched_recipes is not None: 
            return Response(status=status.HTTP_200_OK, data={ 
                'recipes': searched_recipes
            })


        if search_users is not None: 
            users_query.append(search_users)
            return Response(status=status.HTTP_200_OK, data={ 
                'users': users_query
            })

        return Response(status=status.HTTP_200_OK, data=None)        

            


        

    
    

    

            

