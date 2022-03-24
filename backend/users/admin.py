from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):

    def followers_count(self, obj):
        return obj.followers.all().count()

    followers_count.short_description = 'Число подписчиков'

    list_display = (
        'id',
        'username',
        'email',
        'followers_count'
    )
    filter_fields = (
        'username',
        'email',
    )
    ordering = ('id',)
    empty_value_display = '--empty--'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
