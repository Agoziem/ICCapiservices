# Generated by Django 3.2.7 on 2024-06-17 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CBTpractice', '0006_auto_20240531_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='testTime',
        ),
        migrations.AddField(
            model_name='subject',
            name='subjectduration',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]