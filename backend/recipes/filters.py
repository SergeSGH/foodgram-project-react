from django_filters import rest_framework

from .models import Ingredient, Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):

    is_favorited = rest_framework.filters.BooleanFilter(method='favorited')
    is_in_shopping_cart = rest_framework.filters.BooleanFilter(
        method='in_basket'
    )
    tags = rest_framework.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def favorited(self, queryset, field_name, value):
        if value:
            return queryset.filter(favorited__user=self.request.user)
        return queryset

    def in_basket(self, queryset, field_name, value):
        if value:
            return queryset.filter(basket__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    @property
    def qs(self):
        parent = super(RecipeFilter, self).qs
        if (
            not self.request.query_params.getlist('tags')
            and self.request.query_params.getlist('page')
            and not self.request.query_params.getlist('is_in_shopping_cart')
        ):
            return parent.none()
        return parent


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.filters.CharFilter(
        field_name='name',
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
