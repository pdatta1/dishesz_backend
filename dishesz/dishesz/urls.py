
from django.urls import path, include 

urlpatterns = [

    path('users/', include('users.urls')),
    path('recipe/',include('recipe.urls')),
    path('feeds/', include('feeds.urls')),
    path('api/', include('rest_framework.urls')),
    
]
