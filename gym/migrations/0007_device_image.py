# Generated by Django 5.2.3 on 2025-06-15 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0006_finalize_device_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='device_images/'),
        ),
    ]
