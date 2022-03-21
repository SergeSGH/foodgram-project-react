from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Follow

from .models import User

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
        request=self.context.get('request')
        if request.user.is_authenticated:
            if Follow.objects.filter(user=request.user).filter(
                author=obj
            ).exists():
                return True
        return False 

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

