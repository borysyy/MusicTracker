# Generated by Django 5.1.4 on 2025-01-17 04:50

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_artist_genre_album_collection_artist_genre_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_hue',
            field=colorfield.fields.ColorField(default='#000000', image_field=None, max_length=25, samples=None),
        ),
    ]
