# Generated by Django 4.2.10 on 2024-03-08 07:10

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_profile_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='uid',
            field=models.CharField(default=uuid.uuid4, max_length=200),
        ),
    ]
