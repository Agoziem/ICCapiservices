# Generated by Django 3.2.7 on 2024-06-22 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_auto_20240622_1610'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='category',
        ),
    ]
