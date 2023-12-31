# Generated by Django 4.2.3 on 2023-07-23 18:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_shoppingcart_favorite_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='unit',
            new_name='measurement_unit',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='text_description',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='recipeingredient',
            old_name='quantity',
            new_name='amount',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='color_code',
            new_name='color',
        ),
    ]
