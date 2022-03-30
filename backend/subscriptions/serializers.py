from rest_framework import serializers

from recipes.models import User
from recipes.serializers import RecipeSerializerShort
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
        if request.user.is_authenticated:
            return Follow.objects.filter(user=request.user).filter(
                author=obj
            ).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        if 'recipes_limit' in self.context:
            recipes_limit = int(self.context.get('recipes_limit'))
            recipes = obj.recipes.all()[:recipes_limit]
            return RecipeSerializerShort(recipes, many=True).data
        recipes = obj.recipes.all()
        return RecipeSerializerShort(recipes, many=True).data
