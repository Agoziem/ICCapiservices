# Generated by Django 3.2.7 on 2024-07-12 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ICCapp', '0010_auto_20240702_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='tiktoklink',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
