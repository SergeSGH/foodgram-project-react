# Generated by Django 3.0 on 2022-03-22 08:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Ингредиент', max_length=200, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(help_text='Единица измерения', max_length=10, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации рецепта')),
                ('name', models.CharField(help_text='Название рецепта', max_length=200, verbose_name='Название рецепта')),
                ('text', models.TextField(help_text='Описание', verbose_name='Описание')),
                ('image', models.ImageField(upload_to='recipes/', verbose_name='Картинка')),
                ('cooking_time', models.IntegerField(help_text='Время приготовления', verbose_name='Время приготовления')),
                ('author', models.ForeignKey(help_text='Автор', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Тэг', max_length=20, unique=True, verbose_name='Тэг')),
                ('slug', models.SlugField(help_text='Слаг тэга', unique=True, verbose_name='Слаг тэга')),
                ('color', models.CharField(help_text='Цвет', max_length=7, unique=True, verbose_name='Цвет')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
            },
        ),
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_tags', to='recipes.Recipe')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='recipes.Tag')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Тэги рецепта', through='recipes.RecipeTag', to='recipes.Tag', verbose_name='Тэги рецепта'),
        ),
        migrations.CreateModel(
            name='Quantity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=1, help_text='Количество', max_digits=4, verbose_name='Количество')),
                ('name', models.CharField(help_text='Ингредиент', max_length=200, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(help_text='Единица измерения', max_length=10, verbose_name='Единица измерения')),
                ('ingredient', models.ForeignKey(help_text='Ингредиент', on_delete=django.db.models.deletion.CASCADE, related_name='quantity', to='recipes.Ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(help_text='Рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.Recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Количество',
                'verbose_name_plural': 'Количества',
            },
        ),
        migrations.AddConstraint(
            model_name='recipetag',
            constraint=models.UniqueConstraint(fields=('recipe', 'tag'), name='unique_recipetag'),
        ),
        migrations.AddConstraint(
            model_name='quantity',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_q'),
        ),
    ]