# Generated by Django 3.0 on 2022-03-30 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quantity',
            name='amount',
            field=models.DecimalField(decimal_places=1, help_text='Количество', max_digits=5, verbose_name='Количество'),
        ),
    ]