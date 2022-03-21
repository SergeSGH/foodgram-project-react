from django.urls import path, include


urlpatterns = [
    path('', include('subscriptions.urls')),
    path('', include('users.urls')),
    path('', include('recipes.urls')),

]
