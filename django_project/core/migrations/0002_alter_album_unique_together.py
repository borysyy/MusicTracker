# Generated by Django 5.1.4 on 2025-04-08 19:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='album',
            unique_together=set(),
        ),
    ]
