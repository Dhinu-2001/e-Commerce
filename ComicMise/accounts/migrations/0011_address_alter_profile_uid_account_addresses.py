# Generated by Django 4.2.10 on 2024-03-15 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_profile_uid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_title', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('ph_number', models.IntegerField()),
                ('pincode', models.CharField(max_length=50)),
                ('locality', models.CharField(max_length=50)),
                ('address', models.TextField(max_length=500)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('landmark', models.CharField(max_length=50)),
                ('alt_phone_number', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='profile',
            name='uid',
            field=models.CharField(default='<function uuid4 at 0x043D3A48>', max_length=200),
        ),
        migrations.AddField(
            model_name='account',
            name='addresses',
            field=models.ManyToManyField(related_name='account_addresses', to='accounts.address'),
        ),
    ]
