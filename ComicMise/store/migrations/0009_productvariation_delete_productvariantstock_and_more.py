# Generated by Django 4.2.10 on 2024-03-05 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_rename_productvariant_productvariantstock_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductVariation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=50)),
                ('stock', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
        migrations.DeleteModel(
            name='ProductVariantStock',
        ),
        migrations.DeleteModel(
            name='SizeVariant',
        ),
    ]
