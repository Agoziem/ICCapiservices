# Generated by Django 3.2.7 on 2024-07-05 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_orders_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='service_delivered',
            field=models.BooleanField(default=False),
        ),
    ]