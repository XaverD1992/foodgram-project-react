from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class User(AbstractUser):
    """Кастомизированная модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    first_name = models.CharField(
        max_length=settings.USER_NAME_LENGTH,
    )
    last_name = models.CharField(
        max_length=settings.USER_NAME_LENGTH,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=settings.EMAIL_LENGTH,
        unique=True
    )
    username = models.CharField(
        'Логин',
        max_length=settings.USER_NAME_LENGTH,
        unique=True,
        validators=[validate_username, ]
    )
    password = models.CharField(
        max_length=settings.PASSWORD_LENGTH,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
