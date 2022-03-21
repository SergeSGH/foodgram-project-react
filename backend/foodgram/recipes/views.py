import itertools
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, filters, permissions, status, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from fpdf import FPDF
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from rest_framework.response import Response
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


from users.permissions import IsAuthor, ReadOnly
from users.models import User
from .models import Recipe, Ingredient, Tag, IsFavorite, IsInBasket
from .serializers import (
    RecipeSerializer,
    RecipeSerializerShort,
    IngredientSerializer,
    TagSerializer,
    SubscriptionSerializer
)

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (
        ReadOnly,
    )
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (
        ReadOnly,
    )
    pagination_class = None

class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        ReadOnly | IsAuthor,
    )
    # queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags__slug', 'author__id')
    pagination_class = LimitOffsetPagination
    serializer_class = RecipeSerializer
    
    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        queryset = Recipe.objects.all()
        if is_favorited:
            queryset = queryset.filter(__favorite__user=request.user)
        if is_in_shopping_cart:
            queryset = queryset.filter(__basket__user=request.user)    
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    def perform_partial_update(self, serializer):
        serializer = serializer(
            request.user,
            data=request.data,
            partial=True
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
                status=status.HTTP_200_OK
            )

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        permission_classes=(
            permissions.IsAuthenticated,
        ),
    )
    def download_shopping_cart(self, request):
        recipe_list = Recipe.objects.filter(basket__user=request.user)
        recipe_list_print=[]
        for recipe in recipe_list:
            recipe_list_print.append(f'Рецепт: {recipe.name}, автор: {recipe.author.username}')
        ingredients_quantity={}
        for recipe in recipe_list:
            for ingredient in recipe.ingredients.all():
                if ingredient.name+'|'+ingredient.measurement_unit in ingredients_quantity:
                    ingredients_quantity[ingredient.name+'|'+ingredient.measurement_unit] += ingredient.quantity
                else:
                    ingredients_quantity[ingredient.name+'|'+ingredient.measurement_unit] = ingredient.quantity
        ingredient_list_print=[]
        sorted_ingredients_list=sorted(ingredients_quantity)
        for ingredient in sorted_ingredients_list:
            ingr_name=ingredient[:ingredient.find('|')]
            ingr_mu=ingredient[ingredient.find('|') + 1:]


            ingredient_list_print.append(f'{ingr_name}: {ingredients_quantity[ingredient]} {ingr_mu}')
            
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('FontPDF', f'{settings.STATIC_URL}journal-italic-cyrillic.ttf'))
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
        p.drawString(20, height, "Список покупок составлен в приложении Foodgram")
        p.showPage()
        p.save()
        buffer.seek(0)
        
        return FileResponse(buffer, as_attachment=True, filename='shopping_cart.pdf')
        
    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(
            permissions.IsAuthenticated,
        ),
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        serializer = RecipeSerializerShort(recipe)
        if request.method == 'POST':
            if IsInBasket.objects.filter(
                recipe=recipe,
                user=self.request.user
            ).exists():
                return Response(
                'Рецепт уже добавлен в корзину',
                status=status.HTTP_400_BAD_REQUEST
            )
            IsInBasket.objects.create(
                recipe=recipe,
                user=self.request.user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not IsInBasket.objects.filter(
            recipe=recipe,
            user=self.request.user
        ).exists():
            return Response(
            'Рецепта нет в корзине',
            status=status.HTTP_400_BAD_REQUEST
        )
        record = IsInBasket.objects.filter(
            recipe=recipe,
            user=self.request.user
        )
        record.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(
            permissions.IsAuthenticated,
        ),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('pk'))
        print(recipe)
        serializer = RecipeSerializerShort(recipe)
        print(serializer.data)
        if request.method == 'POST':
            if IsFavorite.objects.filter(
                recipe=recipe,
                user=self.request.user
            ).exists():
                return Response(
                'Рецепт уже добавлен в избранное',
                status=status.HTTP_400_BAD_REQUEST
            )
            IsFavorite.objects.create(
                recipe=recipe,
                user=self.request.user
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if not IsFavorite.objects.filter(
            recipe=recipe,
            user=self.request.user
        ).exists():
            return Response(
            'Рецепта нет в избранном',
            status=status.HTTP_400_BAD_REQUEST
        )
        record = IsFavorite.objects.filter(
            recipe=recipe,
            user=self.request.user
        )
        record.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class SubscriptionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, ReadOnly)
    pagination_class = LimitOffsetPagination
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        #return self.request.user.follows.values('author')
        return User.objects.filter(followers__user=self.request.user)
