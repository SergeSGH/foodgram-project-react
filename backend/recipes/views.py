import io
import itertools

from django.conf import settings
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from subscriptions.models import IsFavorite, IsInBasket, Recipe
from users.models import User
from users.permissions import IsAuthor, ReadOnly
from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Tag
from .serializers import (IngredientSerializer, RecipeInputSerializer,
                          RecipeOutputSerializer, RecipeSerializerShort,
                          TagSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (ReadOnly | IsAuthor, IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeInputSerializer
        return RecipeOutputSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    def perform_partial_update(self, obj, serializer):
        serializer = serializer(
            obj, data=self.request.data, partial=True
        )
        serializer.save()

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        recipe_list = Recipe.objects.filter(basket__user=request.user)
        ingredient_list = Ingredient.objects.filter(
            quantity__recipe__in=recipe_list
        ).annotate(for_shopping=Sum('quantity__amount'))

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont(
            'FontPDF', f'{settings.STATIC_ROOT}/'
            + 'journal-italic-cyrillic.ttf')
        )
        p.setFont('FontPDF', 10)
        counter = itertools.count(800, -30)
        height = next(counter)
        p.drawString(20, height, "Список рецептов:")

        counter_n = itertools.count(1, 1)
        for recipe in recipe_list.values('name', 'author'):
            height = next(counter)
            n = next(counter_n)
            recipe_name = recipe['name']
            author = User.objects.get(id=recipe['author'])
            first_name = author.first_name
            last_name = author.last_name
            p.drawString(40, height, f'{n}. Рецепт: {recipe_name}, автор: '
                         + f'{first_name} {last_name}')

        height = next(counter)
        p.drawString(20, height, "Список покупок:")

        counter_n = itertools.count(1, 1)
        for ingredient in ingredient_list.values_list(
            'name',
            'measurement_unit',
            'for_shopping'
        ):
            height = next(counter)
            n = next(counter_n)
            p.drawString(40, height, f'{n}. {ingredient[0]}'
                         + f' ({ingredient[1]}) - {ingredient[2]}')
        height = next(counter)
        p.drawString(20, height, "Приложение Foodgram")
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping_cart.pdf'
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        serializer = RecipeSerializerShort(recipe)
        return self.sub_create_del(request, IsInBasket, serializer, recipe)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        serializer = RecipeSerializerShort(recipe)
        return self.sub_create_del(request, IsFavorite, serializer, recipe)

    def sub_create_del(self, request, model, serializer, recipe):
        if request.method == 'POST':
            if model.objects.filter(
                recipe=recipe, user=self.request.user
            ).exists():
                return Response(
                    'Рецепт уже добавлен в избранное',
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(
                recipe=recipe, user=self.request.user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not model.objects.filter(
            recipe=recipe, user=self.request.user
        ).exists():
            return Response(
                'Рецепта нет в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        record = model.objects.filter(
            recipe=recipe, user=self.request.user
        )
        record.delete()
        return Response(
            'Рецепт удален из избранного',
            status=status.HTTP_204_NO_CONTENT
        )
