# Generated by Django 3.2.7 on 2024-10-20 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ICCapp', '0013_delete_notifications'),
        ('vidoes', '0011_video_number_of_times_bought'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ICCapp.organization'),
        ),
    ]
