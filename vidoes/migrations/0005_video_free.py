# Generated by Django 3.2.7 on 2024-07-16 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vidoes', '0004_auto_20240716_0230'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='free',
            field=models.BooleanField(default=False),
        ),
    ]