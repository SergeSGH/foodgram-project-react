import io
import itertools

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from subscriptions.models import IsFavorite, IsInBasket, Recipe
from users.permissions import IsAuthor, ReadOnly
from .filters import RecipeFilter
from .models import Ingredient, Tag
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeSerializerShort, TagSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        queryset = Ingredient.objects.filter(name__startswith=name)
        return queryset
       

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (ReadOnly | IsAuthor,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination
    serializer_class = RecipeSerializer

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        queryset = Recipe.objects.all()
        if is_favorited:
            queryset = queryset.filter(favorited__user=self.request.user)
        if is_in_shopping_cart:
            queryset = queryset.filter(basket__user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    def perform_partial_update(self, obj, serializer):
        serializer = serializer(
            obj, data=self.request.data, partial=True
        )
        if serializer.is_valid:
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        recipe_list = Recipe.objects.filter(basket__user=request.user)
        recipe_list_print = []
        for recipe in recipe_list:
            recipe_list_print.append(
                f'Рецепт: {recipe.name}, автор: {recipe.author.username}'
            )
        ingredients_quantity = {}
        for recipe in recipe_list:
            for ingredient in recipe.ingredients.all():
                full_ingredient = (
                    ingredient.name + '|' + ingredient.measurement_unit
                )
                if full_ingredient in ingredients_quantity:
                    ingredients_quantity[full_ingredient] += \
                        ingredient.quantity
                else:
                    ingredients_quantity[full_ingredient] = \
                        ingredient.quantity
        ingredient_list_print = []
        sorted_ingredients_list = sorted(ingredients_quantity)
        for ingredient in sorted_ingredients_list:
            ingr_name = ingredient[:ingredient.find('|')]
            ingr_mu = ingredient[ingredient.find('|') + 1:]
            ingredient_list_print.append(
                f'{ingr_name} ({ingr_mu}) - {ingredients_quantity[ingredient]}'
            )
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont(
            'FontPDF', f'- {settings.STATIC_URL}journal-italic-cyrillic.ttf')
        )
        p.setFont('FontPDF', 10)
        counter = itertools.count(650, -30)
        height = next(counter)
        p.drawString(20, height, "Список рецептов")
        for recipe in recipe_list_print:
            height = next(counter)
            p.drawString(20, height, str(recipe))
        height = next(counter)
        p.drawString(20, height, "Список покупок")
        for ingredient in ingredient_list_print:
            height = next(counter)
            p.drawString(20, height, ingredient)
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
        if request.method == 'POST':
            if IsInBasket.objects.filter(
                recipe=recipe, user=self.request.user
            ).exists():
                return Response(
                    'Рецепт уже добавлен в корзину',
                    status=status.HTTP_400_BAD_REQUEST
                )
            IsInBasket.objects.create(
                recipe=recipe, user=self.request.user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not IsInBasket.objects.filter(
            recipe=recipe, user=self.request.user
        ).exists():
            return Response(
                'Рецепта нет в корзине',
                status=status.HTTP_400_BAD_REQUEST
            )
        record = IsInBasket.objects.filter(
            recipe=recipe, user=self.request.user
        )
        record.delete()
        return Response(
            'Рецепт удален из корзины',
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        print(recipe)
        serializer = RecipeSerializerShort(recipe)
        print(serializer.data)
        if request.method == 'POST':
            if IsFavorite.objects.filter(
                recipe=recipe, user=self.request.user
            ).exists():
                return Response(
                    'Рецепт уже добавлен в избранное',
                    status=status.HTTP_400_BAD_REQUEST
                )
            IsFavorite.objects.create(
                recipe=recipe, user=self.request.user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not IsFavorite.objects.filter(
            recipe=recipe, user=self.request.user
        ).exists():
            return Response(
                'Рецепта нет в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        record = IsFavorite.objects.filter(
            recipe=recipe, user=self.request.user
        )
        record.delete()
        return Response(
            'Рецепт удален из избранного',
            status=status.HTTP_204_NO_CONTENT
        )
