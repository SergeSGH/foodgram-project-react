from rest_framework import mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from users.models import User
from users.permissions import IsOwner
from .serializers import SubscriptionSerializer


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    pagination_class = LimitOffsetPagination
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return User.objects.filter(followers__user=self.request.user)
