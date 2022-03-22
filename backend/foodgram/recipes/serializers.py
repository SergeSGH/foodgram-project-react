import base64
import os

from django.conf import settings
from rest_framework import serializers

from subscriptions.models import IsFavorite, IsInBasket
from users.serializers import UserSerializer
from .models import Ingredient, Quantity, Recipe, Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class QuantitySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    
    class Meta:
        model = Quantity
        fields = ('id', 'amount')

#class QuantitySerializer(serializers.ModelSerializer):
#    id = serializers.SlugRelatedField(
#        source='ingredient',
#        queryset=Ingredient.objects.all(),
#        slug_field='id'
#    )
#    
#    class Meta:
#        model = Quantity
#        fields = ('id', 'amount')

#class QuantitySerializer(serializers.Serializer):
#    id = serializers.IntegerField
#    amount = serializers.DecimalField
#
#    def to_representation(self, instance):
#        return {
#            'id': instance.ingredient.id, 
#            'amount': instance.amount
#        }



class B64ToFile(serializers.Field):

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        try:
            separator = data.find(';')
            data_type = data[:10]
            ext = data[11:separator]
            encoding = data[separator + 1:separator + 7]
            image_data = bytes(data[separator + 8:], encoding='utf-8')
            if data_type == 'data:image' and encoding == 'base64':
                i = 0
                while os.path.exists(
                    settings.MEDIA_ROOT + f'recipe_pic_{i}.{ext}'
                ):
                    i += 1
                with open(
                    settings.MEDIA_ROOT + f'recipe_pic_{i}.{ext}', "wb"
                ) as fh:
                    fh.write(base64.decodebytes(image_data))
                return (settings.MEDIA_ROOT + f'recipe_pic_{i}.{ext}')
            raise serializers.ValidationError('Некорректный формат данных')
        except ValueError:
            raise serializers.ValidationError(
                'Не удалось декодировать картинку'
            )


class RecipeSerializerShort(serializers.ModelSerializer):
    image = B64ToFile()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = QuantitySerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = B64ToFile()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_field = ('id', 'author')

    def get_is_favorited(self, obj):
        return IsFavorite.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return IsInBasket.objects.filter(
            user=self.context['request'].user,
            recipe=obj
        ).exists()

    def create_ingredients(self, recipe, ingredients):
        #print(ingredients)
        for ingredient in ingredients:
            #print('печать')
            #print(ingredient)
            #print(ingredient.get('ingredient'))
            Quantity.objects.create(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=Ingredient.objects.get(name=ingredient['ingredient'])
            )
        return recipe

    def create(self, initial_data):
        #print("данные", initial_data)
        ingredients = initial_data.pop('ingredients')
        #print(ingredients)
        tags = initial_data.pop('tags')
        recipe = Recipe.objects.create(**initial_data)
        recipe.tags.set(tags)
        if ingredients:
            self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, obj, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            tags = validated_data.pop('tags')
            for attr, value in validated_data.items():
                setattr(obj, attr, value)
            obj.tags.set(tags)
            obj.save()
            for ingredient in obj.ingredients.all():
                ingredient.delete()
            self.create_ingredients(obj, ingredients)
            return obj
