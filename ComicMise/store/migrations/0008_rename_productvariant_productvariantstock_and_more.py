# Generated by Django 4.2.10 on 2024-03-04 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_rename_name_size_size'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductVariant',
            new_name='ProductVariantStock',
        ),
        migrations.RenameModel(
            old_name='Size',
            new_name='SizeVariant',
        ),
    ]
