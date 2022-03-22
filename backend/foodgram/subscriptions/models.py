from django.db import models

from recipes.models import Recipe
from users.models import User


class IsFavorite(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
        help_text='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited',
        verbose_name='Избранный рецепт',
        help_text='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
            name='unique_fav',
            fields=['user', 'recipe'],
        )]

    def __str__(self):
        return f'fav: {self.user} {self.recipe}'


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follows',
        verbose_name='Подписчик',
        help_text='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор подписки',
        help_text='Автор подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            name='unique_follow',
            fields=['author', 'user'],
        )]

    def __str__(self):
        return f'follow: {self.user} {self.author}'


class IsInBasket(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='basket',
        verbose_name='Пользователь корзины',
        help_text='Пользователь корзины'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='basket',
        verbose_name='Рецепт в корзине',
        help_text='Рецепт в корзине'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [models.UniqueConstraint(
            name='unique_basket',
            fields=['user', 'recipe'],
        )]

    def __str__(self):
        return f'basket: {self.user} {self.recipe}'
