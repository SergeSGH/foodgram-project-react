# Generated by Django 3.0 on 2022-03-19 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20220319_1550'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='quantity',
            name='unique_ingredient',
        ),
    ]
