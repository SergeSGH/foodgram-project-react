from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

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
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
        slug_field='name'
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
        slug_field='measurement_unit'
    )

    class Meta:
        model = Quantity
        fields = ('id', 'amount', 'measurement_unit', 'name')


class RecipeSerializerShort(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class RecipeInputSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = QuantitySerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    author = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

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
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author')
            )
        ]

    def create_ingredients(self, recipe, ingredients):
        ingredient_names = set()
        for ingredient in ingredients:
            name = ingredient['ingredient']
            print(name, ingredients)
            if name in ingredient_names:
                raise serializers.ValidationError(
                    'Не могут быть одинаковые ингредиенты для одного рецепта!'
                )
            if ingredient['amount'] < 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть отрицательным!'
                )
            Quantity.objects.create(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=Ingredient.objects.get(
                    name=ingredient['ingredient']
                )
            )
            ingredient_names.add(name)
        return recipe

    def create(self, vaidated_data):
        ingredients = vaidated_data.pop('ingredients')
        image = vaidated_data.pop('image')
        tags = vaidated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **vaidated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, obj, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(obj, validated_data)
        obj.tags.set(tags)
        obj.save()
        obj.ingredients.all().delete()
        self.create_ingredients(obj, ingredients)
        return obj


class RecipeOutputSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = QuantityOutputSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

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
