# Generated by Django 3.2.7 on 2024-07-16 23:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vidoes', '0008_auto_20240717_0050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vidoes.category'),
        ),
    ]