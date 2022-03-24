from django.contrib import admin
# from django.utils.html import format_html
# from django.conf import settings

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

    inlines = (QuantityInline, TagInline,)
    list_display = (
        'id',
        'author',
        'name',
        'cooking_time',
        'image',
        # 'image_list_preview',
        'favorite_count'
    )
    search_fields = (
        'name',
        'author__username',
        'author__email'
    )
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    empty_value_display = '--empty--'
    # read_only_fields = ('image_change_preview',)

    # пока не настроено
    # def image_change_preview(self, obj):
    #     if obj.image:
    #         url = obj.image.url
    #         print('change', url)
    #         return format_html(
    #             '<img scr="{}" width="600" height="300" style="'
    #             "border: 2px solid grey;"
    #             'border-radius:50px;" />'.format(url)
    #         )
    #     return "Превью"

    # image_change_preview.short_description = "Превью"

    # def image_list_preview(self, obj):
    #     if obj.image:
    #         url = obj.image.url[len(settings.MEDIA_URL)*2-2:]
    #         print('preview', url,type(url))
    #         return format_html(
    #             '<img scr="{}" width="100" height="50" style="'
    #             "border: 1px solid grey;"
    #             'border-radius:10px;" />',format(url)
    #         )
    #     return "Картинка"

    # image_list_preview.short_description = "Картинка"


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
