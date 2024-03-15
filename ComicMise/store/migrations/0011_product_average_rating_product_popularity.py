# Generated by Django 4.2.10 on 2024-03-15 08:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_remove_product_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='average_rating',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AddField(
            model_name='product',
            name='popularity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]