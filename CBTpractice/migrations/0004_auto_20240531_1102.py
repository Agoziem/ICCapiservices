# Generated by Django 3.2.7 on 2024-05-31 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CBTpractice', '0003_remove_test_testmark'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='questions',
        ),
        migrations.AddField(
            model_name='subject',
            name='questions',
            field=models.ManyToManyField(to='CBTpractice.Question'),
        ),
    ]