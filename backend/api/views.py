from django.conf import settings
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import CustomizedPaginator
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeGetSerializer,
                             ShoppingCartSerializer, SubscribeSerializer,
                             TagSerializer, UserSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class CustomUserViewSet(UserViewSet):
    """Вьюсет для кастомной модели пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomizedPaginator

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        """Подписка/отписка на пользователя."""
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            serializer = SubscribeSerializer(author,
                                             data=request.data,
                                             context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        get_object_or_404(Subscription, user=request.user,
                          author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Список подписок пользователя."""
        return self.get_paginated_response(
            SubscribeSerializer(
                self.paginate_queryset(
                    User.objects.filter(following__user=request.user)
                ),
                many=True,
                context={'request': request},
            ).data
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации о тегах."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации об ингредиентах."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    pagination_class = None
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Этот Viewset обрабатывает: все стандартные методы ModelViewset +
    добавление/удаление рецептов в Избранное + добавление/удаление/скачивание
    Списка Покупок.
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    pagination_class = CustomizedPaginator
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'create', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post',],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        """Удалить/добавить в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(data={'user': request.user.id,
                                              'recipe': recipe.id, },
                                        context={"request": request})
        serializer.is_valid(raise_exception=True)
        if not Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже в избранном.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post',],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        """Удалить/добавить в список покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShoppingCartSerializer(data={'user': request.user.id,
                                                  'recipe': recipe.id, },
                                            context={"request": request})
        serializer.is_valid(raise_exception=True)
        if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже в списке покупок.'},
                        status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def get_file(ingredients):
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (f'attachment; '
                                           f'filename={settings.FILE_NAME}')
        return response

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        return self.get_file(ingredients)
