# Generated by Django 3.2.7 on 2024-05-23 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ICCapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Notification_group', models.CharField(blank=True, choices=[('admin', 'admin'), ('dashboard', 'dashboard'), ('All', 'All')], max_length=100)),
                ('headline', models.CharField(blank=True, max_length=100)),
                ('Notification', models.TextField(blank=True)),
                ('Notificationdate', models.DateField(auto_now_add=True, null=True)),
                ('last_updated_date', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ICCapp.organization')),
                ('users_seen', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
