from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        help_text='Ингредиент',
        max_length=200
        # primary_key=True,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        help_text='Единица измерения',
        max_length=10
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        models.UniqueConstraint(
            name='unique_ingredient',
            fields=['name', 'measurement_unit']
        )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Тэг',
        help_text='Тэг',
        max_length=20,
        unique=True
    )
    slug = models.SlugField(
        'Слаг тэга',
        help_text='Слаг тэга',
        unique=True
    )
    color = models.CharField(
        'Цвет',
        help_text='Цвет',
        max_length=7,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True
    )
    name = models.CharField(
        'Название рецепта',
        help_text='Название рецепта',
        max_length=200
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор'
    )
    text = models.TextField(
        'Описание',
        help_text='Описание',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
    )
    cooking_time = models.IntegerField(
        'Время приготовления',
        help_text='Время приготовления'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тэги рецепта',
        help_text='Тэги рецепта'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    class Meta:
        constraints = (models.UniqueConstraint(
            name='unique_recipetag',
            fields=('recipe', 'tag')
        ),)

    def __str__(self):
        return f'{self.recipe} {self.tag}'



class Quantity(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='quantity',
        verbose_name='Ингредиент',
        help_text='Ингредиент'
    )
    quantity = models.DecimalField(
        'Количество',
        decimal_places=1,
        max_digits=4,
        help_text='Количество'
    )
    name = models.CharField(
        'Ингредиент',
        help_text='Ингредиент',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        help_text='Единица измерения',
        max_length=10
    )


    class Meta:
        verbose_name = 'Количество'
        verbose_name_plural = 'Количества'
        constraints = [models.UniqueConstraint(
            name='unique_q',
            fields=['recipe', 'ingredient'],
        )]

    #@property
    #def name(self):
    #    return self.ingredient.name

    #@property
    #def measurement_unit(self):
    #    return self.ingredient.measurement_unit

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


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
