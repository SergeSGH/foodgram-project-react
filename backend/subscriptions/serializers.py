from rest_framework import serializers

from recipes.serializers import RecipeSerializerShort
from users.models import User
from .models import Follow


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if obj.is_authenticated:
            return Follow.objects.filter(user=request.user).filter(
                author=obj
            ).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = obj.recipes.all()[:recipes_limit]
        return RecipeSerializerShort(recipes, many=True).data
