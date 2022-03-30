from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from recipes.models import User
from subscriptions.models import Follow
from subscriptions.serializers import SubscriptionSerializer
from .serializers import SetPassSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (
        permissions.AllowAny,
    )
    pagination_class = PageNumberPagination
    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = ('username',)

    @action(
        detail=False,
        methods=('get',),
        url_path='me',
        permission_classes=(
            permissions.IsAuthenticated,
        ),
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=('post',),
        url_path='set_password',
        permission_classes=(
            permissions.IsAuthenticated,
        ),
    )
    def set_password(self, request):
        serializer = SetPassSerializer(data=request.data)
        user = request.user
        serializer.is_valid(raise_exception=True)
        if user.check_password(request.data.get('current_password')):
            user.set_password(request.data.get('new_password'))
            user.save()
            return Response(
                data=serializer.data, status=status.HTTP_200_OK
            )
        else:
            return Response(
                'некорректный пароль', status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(
            permissions.IsAuthenticated,
        ),
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=self.kwargs.get('pk'))
        if request.method == 'POST':
            if Follow.objects.filter(
                author=author,
                user=self.request.user
            ).exists():
                return Response(
                    'На автора уже есть подписка',
                    status=status.HTTP_400_BAD_REQUEST
                )
            if author == self.request.user:
                return Response(
                    'Нельзя подписаться на самого себя',
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(
                author=author,
                user=self.request.user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not Follow.objects.filter(
            author=author,
            user=self.request.user
        ).exists():
            return Response(
                'Подписки нет',
                status=status.HTTP_400_BAD_REQUEST
            )
        record = Follow.objects.filter(
            author=author,
            user=self.request.user
        )
        record.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
