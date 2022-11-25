
from django.urls import path, include 

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


from users.views import ( 
    DisheszUserAPI, 
    CreateUserAPI, 
    VerifyEmail, 
    ChangeEmailAPI, 
    ResetPasswordAPI,
    HandleForgotPassword, 
    DeleteAccountAPI,
    FollowUserAPI, 
    unFollowUserAPI,
    UserFollowersAPI, 
    UserFollowingAPI,

    )


user_router = DefaultRouter() 
user_router.register(r'dishesz_user', DisheszUserAPI, basename='dishesz_user')
user_router.register('create_user', CreateUserAPI, basename='create_user')
user_router.register('change_email', ChangeEmailAPI, basename='change_email')
user_router.register('handle_forgot_password', HandleForgotPassword, basename='handle_forgot_password')
user_router.register('reset_password', ResetPasswordAPI, basename='reset_password')
user_router.register('verify', VerifyEmail, basename='verify')
user_router.register('delete_account', DeleteAccountAPI, basename='delete_account')
user_router.register('follow_user', FollowUserAPI, basename='follow_user')
user_router.register('unfollow_user', unFollowUserAPI, basename='unfollow_user')
user_router.register('user_followers', UserFollowersAPI, basename='user_followers')
user_router.register('user_followings', UserFollowingAPI, basename='user_followings')


app_name = 'users'

urlpatterns = [ 
    path('', include(user_router.urls)),
    path('access/', TokenObtainPairView.as_view(), name='access'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
]