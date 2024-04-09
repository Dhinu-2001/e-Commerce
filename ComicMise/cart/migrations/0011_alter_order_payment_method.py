# Generated by Django 4.2.10 on 2024-04-08 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0010_alter_order_is_returned'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('COD', 'Cash on Delivery'), ('Wallet', 'Wallet'), ('Razorpay', 'Razorpay')], default='COD', max_length=20),
        ),
    ]