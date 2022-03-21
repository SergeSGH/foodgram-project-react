from django.urls import include, path
#from rest_framework.routers import DefaultRouter
#from .routers import SubscriptionsRouter

from recipes.views import SubscriptionViewSet

#router = SubscriptionsRouter()
#router = DefaultRouter()
#router.register('users/subscriptions', SubscriptionViewSet, basename='subscriptions')

#urlpatterns = (
#    path('', include(router.urls)),
#)


urlpatterns = (
    path('users/subscriptions/', SubscriptionViewSet.as_view({'get': 'list'})),
)
