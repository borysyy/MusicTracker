# Generated by Django 5.1.4 on 2025-01-27 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_user_profile_hue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_hue',
            field=models.CharField(default='#000000', max_length=7),
        ),
    ]
