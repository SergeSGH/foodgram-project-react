from django.contrib import admin

from .models import Ingredient, Quantity, Recipe, RecipeTag, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = ('measurement_unit',)
    search_fields = (
        'name',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color',
    )
    filter_fields = (
        'name',
        'slug',
        'color',
    )
    empty_value_display = '--empty--'


class QuantityInline(admin.StackedInline):
    model = Quantity
    extra = 0


class TagInline(admin.StackedInline):
    model = RecipeTag
    extra = 0


class RecipeAdmin(admin.ModelAdmin):

    def favorite_count(self, obj):
        return obj.favorited.all().count()

    favorite_count.short_description = 'Добавлено в избранное'

    inlines = [QuantityInline, TagInline]
    list_display = (
        'id',
        'author',
        'name',
        'cooking_time',
        'image',
        'favorite_count'
    )
    search_fields = (
        'name',
        'author'
    )
    ordering = ('id',)
    empty_value_display = '--empty--'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
