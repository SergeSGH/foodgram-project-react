from django.contrib import admin

from .models import Follow, IsFavorite, IsInBasket


class IsFavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('recipe__name',)
    filter_fields = ('user__username',)
    ordering = ('user',)
    empty_value_display = '--empty--'


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user__username',)
    filter_fields = (
        'user__username',
        'author__username',
    )
    ordering = ('user',)
    empty_value_display = '--empty--'


class IsInBasketAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('recipe__name',)
    filter_fields = ('user__username',)
    ordering = ('user',)
    empty_value_display = '--empty--'


admin.site.register(IsFavorite, IsFavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(IsInBasket, IsInBasketAdmin)
