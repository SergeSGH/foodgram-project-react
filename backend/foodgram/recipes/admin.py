from django.contrib import admin

from .models import Ingredient, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = (
        'name',
    )

class RecipeAdmin(admin.ModelAdmin):
    list_display = (

        'id',
        'name',
        'author',
        'text',
        'image',
        'cooking_time',
    )
    search_fields = (
        'name',
        'author',
        'tag',
    )
    #list_editable = (
    #    'name',
    #    'author',
    #    'text',
    #    'image',
    #    'cooking_time',
    #)
    empty_value_display = '--empty--'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color',
    )
    search_fields = (
        'name',
        'slug',
        'color',
    )
    #list_editable = (
    #    'name',
    #    'slug',
    #    'color',
    #)
    empty_value_display = '--empty--'


    def genre_display(self, object):
        return object.genre

    genre_display.empty_value_display = '--empty--'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
