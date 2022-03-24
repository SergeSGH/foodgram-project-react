import base64
import os

from django.conf import settings
from rest_framework import serializers

from subscriptions.models import IsFavorite, IsInBasket
from users.serializers import UserSerializer
from .models import Ingredient, Quantity, Recipe, RecipeTag, Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')
        read_only_fields = ('name', 'slug', 'color',)


class QuantitySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = Quantity
        fields = ('id', 'amount')


class QuantityOutputSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Quantity
        fields = ('id', 'amount', 'measurement_unit', 'name')

    def get_id(self, obj):
        return obj.ingredient.id

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    def get_name(self, obj):
        return obj.ingredient.name


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
                    settings.MEDIA_URL[1:]
                    + 'recipes/'
                    + f'recipe_pic_{i}.{ext}'
                ):
                    i += 1
                with open(
                    settings.MEDIA_URL[1:]
                    + 'recipes/'
                    + f'recipe_pic_{i}.{ext}', "wb"
                ) as fh:
                    fh.write(base64.decodebytes(image_data))
                return (
                    settings.MEDIA_URL[1:]
                    + 'recipes/'
                    + f'recipe_pic_{i}.{ext}'
                )
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


class TagsField(serializers.Field):

    def to_representation(self, value):
        new_tags = []
        for tag in value:
            new_tags.append({
                'id': getattr(tag, 'id'),
                'name': getattr(tag, 'name'),
                'slug': getattr(tag, 'slug'),
                'color': getattr(tag, 'color'),
            })
        return new_tags

    def to_internal_value(self, data):
        recipe_tag_list = []
        for tag in data:
            new_recipe_tag = RecipeTag.objects.create(
                recipe=self.instance, tag=tag
            )
            new_recipe_tag.save()
            recipe_tag_list.append(new_recipe_tag)
        return recipe_tag_list


class RecipeInputSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = QuantitySerializer(many=True)
    author = UserSerializer(read_only=True)
    image = B64ToFile()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_field = ('id', 'author')

    def create_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            Quantity.objects.create(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=Ingredient.objects.get(
                    name=ingredient['ingredient']
                )
            )
        return recipe

    def create(self, vaidated_data):
        ingredients = vaidated_data.pop('ingredients')
        image = vaidated_data.pop('image')
        tags = vaidated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **vaidated_data)
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


class RecipeOutputSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = QuantityOutputSerializer(many=True)
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

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return IsFavorite.objects.filter(
                user=user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return IsInBasket.objects.filter(
                user=user, recipe=obj
            ).exists()
        return False
