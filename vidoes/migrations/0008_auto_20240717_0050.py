# Generated by Django 3.2.7 on 2024-07-16 23:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vidoes', '0007_auto_20240716_2200'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subcategory', models.CharField(max_length=100)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vidoes.category')),
            ],
            options={
                'verbose_name_plural': 'SubCategories',
            },
        ),
        migrations.AddField(
            model_name='video',
            name='subcategory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vidoes.subcategory'),
        ),
    ]
