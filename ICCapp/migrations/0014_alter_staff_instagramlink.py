# Generated by Django 3.2.7 on 2024-10-21 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ICCapp', '0013_delete_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='instagramlink',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]