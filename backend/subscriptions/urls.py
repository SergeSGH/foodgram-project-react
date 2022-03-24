from django.urls import path

from .views import SubscriptionViewSet

urlpatterns = (
    path('users/subscriptions/', SubscriptionViewSet.as_view({'get': 'list'})),
)
