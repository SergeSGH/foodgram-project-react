from django.contrib import admin

from .models import Follow, IsFavorite, IsInBasket


class IsFavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    filter_fields = (
        'user',
        'recipe',
    )
    empty_value_display = '--empty--'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    filter_fields = (
        'user',
        'author',
    )
    empty_value_display = '--empty--'


class IsInBasketAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    filter_fields = (
        'user',
        'recipe',
    )
    empty_value_display = '--empty--'


admin.site.register(IsFavorite, IsFavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(IsInBasket, IsInBasketAdmin)
