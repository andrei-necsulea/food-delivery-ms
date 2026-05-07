# Generated manually: add location_label and location_code to Delivery
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0004_delivery_current_latitude_delivery_current_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='location_label',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='delivery',
            name='location_code',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
