# Generated by Django 4.2.10 on 2024-04-09 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0046_alter_profile_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='uid',
            field=models.CharField(default='<function uuid4 at 0x03D03A00>', max_length=200),
        ),
    ]