from django.db import models

from users.models import User


class Ingredient(models.Model):
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
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        models.UniqueConstraint(
            name='unique_ingredient',
            fields=['name', 'measurement_unit']
        )
        ordering = ('id',)

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
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецепта'
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
    amount = models.DecimalField(
        'Количество',
        decimal_places=1,
        max_digits=4,
        help_text='Количество'
    )


    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиент рецепта'
        constraints = [models.UniqueConstraint(
            name='unique_q',
            fields=['recipe', 'ingredient'],
        )]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'
