# Generated by Django 3.2.7 on 2024-06-27 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ICCapp', '0007_auto_20240620_0341'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_date', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ICCapp.organization')),
            ],
        ),
        migrations.CreateModel(
            name='DepartmentService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
        migrations.AddField(
            model_name='department',
            name='services',
            field=models.ManyToManyField(blank=True, to='ICCapp.DepartmentService'),
        ),
        migrations.AddField(
            model_name='department',
            name='staff_in_charge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ICCapp.staff'),
        ),
    ]
