from rest_framework import serializers

from recipes.models import User
from subscriptions.models import Follow


class SetPassSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'password'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Follow.objects.filter(user=request.user).filter(
                author=obj
            ).exists()
        return False

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
