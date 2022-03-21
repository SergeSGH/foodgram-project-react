from django.conf import settings

from rest_framework import serializers

from .models import Ingredient, Tag, Recipe, Quantity, IsFavorite, IsInBasket, Follow

from users.serializers import UserSerializer

from users.models import User

import base64, os


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


#class QuantitySerializer(serializers.Serializer):
#    name = serializers.CharField(required=True)
#    measurement_unit = serializers.CharField(required=False)
#    quantity = serializers.DecimalField(
#        decimal_places=1, max_digits=4
#    )

#class CustomNameField(serializers.Field):
#    def to_representation(self, instance):
#        return 1
#    def to_internal_value(self, data):
#        return data


#class CustomMUField(serializers.Field):
#    def to_representation(self, instance):
#        return 1
#    def to_internal_value(self, data):
#        return data

class QuantitySerializer(serializers.ModelSerializer):
    #name = serializers.SlugRelatedField(queryset=Ingredient.objects.all, slug_field='name')

    #name = CustomNameField()
    #measurement_unit = CustomMUField()


    class Meta:
        model = Quantity
        fields = ('name', 'quantity', 'measurement_unit')
        #extra_kwargs = {'name': {'write_only': True}}


#class QuantitySerializer(serializers.ModelSerializer):
    #name = serializers.SerializerMethodField()
    #measurement_unit = serializers.SerializerMethodField()

    #name = CustomNameField()
    #measurement_unit = CustomMUField()


#    class Meta:
#        model = Quantity
#        fields = ('name', 'measurement_unit', 'quantity')
        #extra_kwargs = {'name': {'write_only': True}}

    #def to_representation(self, instance):
    #    representation = super().to_representation(instance)
    #    representation['name'] = instance.ingredient.name
    #    representation['measurement_unit'] = instance.ingredient.measurement_unit
    #    return representation

    #def get_name(self, obj):
    #    return obj.ingredient.name

    #def get_measurement_unit(self, obj):
    #    return obj.ingredient.measurement_unit

class B64ToFile(serializers.Field):
    def to_representation(self, value):
        return str(value)
    def to_internal_value(self, data):
        try:
            separator = data.find(';')
            data_type = data[:10]
            ext = data[11:separator]
            encoding = data[separator+1:separator+7]
            print(data[separator+8:])
            image_data = bytes(data[separator+8:], encoding='utf-8')
            print(image_data)
            if data_type == 'data:image' and encoding == 'base64':
                i = 0
                while os.path.exists(settings.MEDIA_ROOT + f'recipe_pic_{i}.{ext}'):
                    i += 1
                with open(settings.MEDIA_ROOT + f'recipe_pic_{i}.{ext}', "wb") as fh:
                    fh.write(base64.decodebytes(image_data))
                print('записали')
                return (settings.MEDIA_ROOT + f'recipe_pic_{i}.{ext}')
            raise serializers.ValidationError('Некорректный формат данных')
        except ValueError:
            raise serializers.ValidationError('Не удалось декодировать картинку')



class IngredientsSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    measurement_unit = serializers.CharField(read_only=True)
    quantity = serializers.DecimalField(decimal_places=1, max_digits=4)

    def get_name(self, instance):
        return instance.ingredient.name

    def get_measurement_unit(self, instance):
        return instance.ingredient.measurement_unit    


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
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

    def create(self, initial_data):
        ingredients = initial_data.pop('ingredients')
        print(ingredients)
        tags = initial_data.pop('tags')
        recipe = Recipe.objects.create(**initial_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            print(ingredient)
            if Ingredient.objects.filter(name=ingredient['name']).filter(measurement_unit=ingredient['measurement_unit']).exists():
                current_ingredient = Ingredient.objects.get(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )
                print(current_ingredient)
                print(recipe)
                print(ingredient['quantity'])
                Quantity.objects.create(
                    ingredient=current_ingredient,
                    recipe=recipe,
                    quantity=ingredient['quantity'],
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit'],
                )
                print('created')
            else:
                current_ingredient = Ingredient.objects.create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )
                current_ingredient.save()
                Quantity.objects.create(
                    ingredient=current_ingredient,
                    recipe=recipe,
                    quantity=ingredient['quantity'],
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit'],
                )
        return recipe

    def update(self, obj, initial_data):
        if 'ingredients' in initial_data:
            ingredients = initial_data.pop('ingredients')
            for attr, value in initial_data.items():
                setattr(obj, attr, value)
            obj.save()


            #serialiser = self.get_serializer(obj, initial_data, partial=True)
            #serializer.save
            for ingredient in obj.ingredients.all():
                ingredient.delete()
            for ingredient in ingredients:
                if Ingredient.objects.filter(name=ingredient['name']).filter(measurement_unit=ingredient['measurement_unit']).exists():
                    current_ingredient = Ingredient.objects.get(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit']
                    )
                    Quantity.objects.create(
                        ingredient=current_ingredient,
                        recipe=obj,
                        quantity=ingredient['quantity'],
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit'],
                    )
    
                else:
                    current_ingredient = Ingredient.objects.create(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit']
                    )
                    current_ingredient.save()
                    Quantity.objects.create(
                        ingredient=current_ingredient,
                        recipe=recipe,
                        quantity=ingredient['quantity'],
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit'],
                    )
        else:
            serialiser = self.get_serializer(obj, initial_data, partial=True)
            serializer.save
        return obj

class RecipeSerializerShort(serializers.ModelSerializer):
    #image = B64ToFile()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            #'image',
            'cooking_time'
        )


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
        request=self.context.get('request')
        #print(self.context)
        if obj.is_authenticated:
            if Follow.objects.filter(user=request.user).filter(
                author=obj
            ).exists():
                return True
        return False 
        
    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit=self.context.get('recipes_limit')
        recipes = obj.recipes.all()[:recipes_limit]
        return RecipeSerializerShort(recipes, many=True).data