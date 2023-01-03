
from users.models import (

    DisheszUserProfile, 
    DisheszUserFollowing, 
    DisheszUserFollowers,
    InterestContainer,
    Interest
)

from recipe.models import Recipe 
from recipe.serializers import RecipeSerializer

class LookupUserProfileEssentials(object): 

    """
        @purpose: 
            - LookupUserProfile allows users to view a user profile data
              by a search of their username

    """

    serialized_data = {}

    def add_to_serializer(self, key, value): 
        self.serialized_data[key] = value 

    def get_serialized_data(self): 
        return self.serialized_data


    def get_user_profile(self, user_model): 

        """
            get user profile by matching the user_model with the DisheszUserProfile dishesz_user
            @return yield user_profile
        """

        if user_model: 
            user_profile = DisheszUserProfile.objects.get(dishesz_user=user_model)
            return user_profile 

    
    def get_followings(self, user_model): 
        """
            get the user followings by matching the user_model with the DisheszUserFollowing dishesz_user
            @return yield generator of user.user_follow.username
        """

        followings = DisheszUserFollowing.objects.filter(dishesz_user=user_model)

        for user in followings: 
            yield user.user_follow.username


    def get_followers(self, user_model): 
        """
            get the user followers by matching the user_model with the DisheszUserFollowers dishesz_user
            @return yield generator of user.follower.username
        """

        followers = DisheszUserFollowers.objects.filter(dishesz_user=user_model)

        for user in followers: 
            yield user.follower.username

    def get_interests(self, user_model): 

        """
            get the user interests by matching the user_model with the InterestContainer dishesz_user,
            and filtering all interests that belongs to such container 
            @return yield generator of interest.interest_name

        """

        container = InterestContainer.objects.get(dishesz_user=user_model)
        if container: 
            interests = Interest.objects.filter(container=container)
            for interest in interests: 
                yield interest.interest_name


    def get_saved_recipes(self, user_model): 

        recipes = Recipe.objects.filter(saved_recipes__user=user_model)
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data 



    def get_recipes(self, user_model): 

        """
            get the user recipes by matching the user_model with the Recipe author,
            and serializing the recipes objects

            @return serializer data from RecipeSerializer
        """


        recipes = Recipe.objects.filter(author=user_model)
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data 

    
    def serialized_response_data(self, user_model): 
        """
            assign all the getters of the LookupUserProfile class such as get_user_profile, get_followings, etc.
            add all assigned variables to the add_to_serializer method with the params: (key, value)
        """

        user_profile = self.get_user_profile(user_model)
        user_followings = list(self.get_followings(user_model))
        user_followers = list(self.get_followers(user_model))
        user_interests = list(self.get_interests(user_model))
        user_recipes = self.get_recipes(user_model)
        user_saved_recipes = self.get_saved_recipes(user_model)


        self.add_to_serializer("username", user_model.username)
        self.add_to_serializer("profile_pic", user_profile.get_profile_pic_src())
        self.add_to_serializer("followings", user_followings)
        self.add_to_serializer("followers", user_followers)
        self.add_to_serializer("interests", user_interests)
        self.add_to_serializer("recipes", user_recipes)
        self.add_to_serializer("likes", user_saved_recipes)
