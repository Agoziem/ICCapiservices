# Generated by Django 3.2.7 on 2024-06-11 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ICCapp', '0003_auto_20240610_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='facebooklink',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='staff/images'),
        ),
        migrations.AddField(
            model_name='staff',
            name='role',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='twitterlink',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='staff',
            name='whatsapplink',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
