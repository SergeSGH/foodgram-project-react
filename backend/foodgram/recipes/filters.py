from django_filters import rest_framework

from .models import Recipe, Tag


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    #author = rest_framework.filters.CharFilter(
    #    field_name='author__id',
    #)

    class Meta:
        model = Recipe
        fields = ('tags','author')
