# Generated by Django 5.1.2 on 2024-12-13 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Property_app', '0002_remove_property_image_of_prop_alter_property_owner_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propertyimage',
            name='caption',
        ),
        migrations.AddField(
            model_name='propertyimage',
            name='main',
            field=models.BooleanField(default='False'),
        ),
    ]
