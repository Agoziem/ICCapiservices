# Generated by Django 3.2.7 on 2024-05-31 10:45

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CBTpractice', '0004_auto_20240531_1102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='answer',
            name='isCorrect',
        ),
        migrations.AddField(
            model_name='question',
            name='correctAnswer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='correct_answer', to='CBTpractice.answer'),
        ),
        migrations.AddField(
            model_name='question',
            name='correctAnswerdescription',
            field=ckeditor.fields.RichTextField(blank=True, default='None', null=True),
        ),
    ]