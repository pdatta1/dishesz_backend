from django.urls import path, include 

from rest_framework.routers import DefaultRouter

from feeds.views import ( 
    EstablishUserInterestAPI,
    GenerateUserFeeds,
)

feeds_router = DefaultRouter()

feeds_router.register(r'establish_interest', EstablishUserInterestAPI, basename='establish_interest')
feeds_router.register(r'user_feeds', GenerateUserFeeds, basename='user_feeds')


app_name = 'feeds'
urlpatterns = [ 

    path('', include(feeds_router.urls)),
]