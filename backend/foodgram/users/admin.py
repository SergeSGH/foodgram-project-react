from django.contrib import admin

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email'
    )
    search_fields = (
        'username',
        'email',
    )
    empty_value_display = '--empty--'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
