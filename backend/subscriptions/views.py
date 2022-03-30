from rest_framework import mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from recipes.models import User
from users.permissions import IsOwner
from .serializers import SubscriptionSerializer


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    pagination_class = LimitOffsetPagination
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return User.objects.filter(followers__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {'recipes_limit': self.request.query_params.get('recipes_limit')}
        )
        return context
