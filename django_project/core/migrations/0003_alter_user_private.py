# Generated by Django 5.1.4 on 2025-01-14 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='private',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
