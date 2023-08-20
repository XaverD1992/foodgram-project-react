from django.db import transaction
from drf_base64.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для всех пользователей."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, author):
        """Проверка подписки пользователей."""
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.follower.filter(author=author).exists())


class RecipeSerializer(serializers.ModelSerializer):
    """Список рецептов без ингридиентов."""
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscribeRepresentSerializer(UserSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)
        read_only_fields = ('email', 'username', 'last_name', 'first_name',)

    def get_recipes_count(self, obj):
        """Получение количества рецептов."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Получение рецептов."""
        recipes = obj.recipes.all()
        return RecipeSerializer(recipes, many=True).data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки/отписки от пользователей."""
    class Meta:
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return SubscribeRepresentSerializer(
            instance.author, context={'request': request}
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    """Получение списка или одного ингрединета."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Получение списка или одного тега."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации об ингредиентах."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о рецептах."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientGetSerializer(many=True, read_only=True,
                                          source='recipeingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favorites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favorites.filter(recipe=obj).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления/обновления рецепта."""
    ingredients = IngredientPostSerializer(
        many=True, source='recipeingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        """Проверка ингредиентов."""
        if len(value) <= 0:
            raise serializers.ValidationError(
                'Количество не может быть меньше 1'
            )
        ingredients_id_list = [item['id'] for item in value]
        if len(set(ingredients_id_list)) != len(ingredients_id_list):
            raise serializers.ValidationError(
                'Нельзя вводить одинаковые игредиенты'
            )
        return value

    def validate(self, data):
        """Проверка тегов и времени готовки."""
        tags = data.get('tags')
        if len(tags) != len(set([item for item in tags])):
            raise serializers.ValidationError({
                'tags': 'Тэги не должны повторяться!'})

        cooking_time = data.get('cooking_time')
        if cooking_time > 300 or cooking_time < 1:
            raise serializers.ValidationError({
                'Время приготовления блюда от 1 до 300 минут'
            })
        return data

    @staticmethod
    def set_ingredients(ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_list)

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).clear()
        self.set_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(
            instance,
            context={'request': request}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранными рецептами."""
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для работы со списком покупок."""
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]
