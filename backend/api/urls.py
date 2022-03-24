from django.urls import include, path

urlpatterns = [
    path('', include('subscriptions.urls')),
    path('', include('users.urls')),
    path('', include('recipes.urls')),
]
