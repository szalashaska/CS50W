# Generated by Django 4.0.1 on 2022-01-31 08:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listings',
            old_name='seller',
            new_name='author',
        ),
    ]
