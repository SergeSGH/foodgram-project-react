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
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from subscriptions.models import IsFavorite, IsInBasket, Recipe
from users.permissions import IsAuthor, ReadOnly
from .filters import RecipeFilter
from .models import Ingredient, Tag
from .serializers import (IngredientSerializer, RecipeInputSerializer,
                          RecipeOutputSerializer, RecipeSerializerShort,
                          TagSerializer)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Ingredient.objects.filter(name__startswith=name)
        return super().get_queryset()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (ReadOnly | IsAuthor, IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeInputSerializer
        return RecipeOutputSerializer

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
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
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
                f'Рецепт: {recipe.name}, автор: {recipe.author.first_name} {recipe.author.last_name}'
            )
        ingredients_quantity = {}
        for recipe in recipe_list:
            for ingredient in recipe.ingredients.all():
                ingredient_name = ingredient.ingredient.name
                if ingredient_name in ingredients_quantity:
                    ingredients_quantity[ingredient_name] += \
                        ingredient.amount
                else:
                    ingredients_quantity[ingredient_name] = \
                        ingredient.amount
        ingredient_list_print = []
        sorted_ingredients_list = sorted(ingredients_quantity)
        for ingredient in sorted_ingredients_list:
            ingr_mu = getattr(Ingredient.objects.get(name=ingredient), 'measurement_unit')
            ingredient_list_print.append(
                f'{ingredient} ({ingr_mu}) - {ingredients_quantity[ingredient]}'
            )
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont(
            'FontPDF', f'{settings.STATIC_ROOT}\journal-italic-cyrillic.ttf')
        )
        p.setFont('FontPDF', 10)
        counter = itertools.count(800, -30)
        height = next(counter)
        p.drawString(20, height, "Список рецептов")
        for recipe in recipe_list_print:
            height = next(counter)
            p.drawString(40, height, str(recipe))
        height = next(counter)
        p.drawString(20, height, "Список покупок")
        for ingredient in ingredient_list_print:
            height = next(counter)
            p.drawString(40, height, ingredient)
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
