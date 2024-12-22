# Generated by Django 5.1.2 on 2024-12-22 11:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Property_app', '0007_lease_buyer_property_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lease', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='Property_app.lease')),
            ],
        ),
    ]
