# Generated by Django 3.2.7 on 2024-07-16 01:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_rename_usersid_that_purchased_product_product_userids_that_bought_this_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='video_token',
            new_name='product_token',
        ),
    ]
