# Generated manually for Order contact and payment fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_alter_order_status_alter_order_total_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Cash'), ('card', 'Card'), ('online', 'Online')], default='cash', max_length=20),
        ),
    ]
