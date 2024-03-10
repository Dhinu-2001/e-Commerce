# Generated by Django 4.2.10 on 2024-03-10 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_profile_otp_expiry_alter_profile_uid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='is_staff',
            new_name='is_user',
        ),
        migrations.RemoveField(
            model_name='account',
            name='is_superadmin',
        ),
        migrations.AlterField(
            model_name='profile',
            name='uid',
            field=models.CharField(default='<function uuid4 at 0x04093A48>', max_length=200),
        ),
    ]
