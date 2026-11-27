"""Makes the database cache's table (settings.CACHES), so "migrate" is enough when deploying."""
from django.core.management import call_command
from django.db import migrations


def create_cache_table(apps, schema_editor):
    call_command('createcachetable', database=schema_editor.connection.alias)


class Migration(migrations.Migration):
    dependencies = [
        ('gym', '0007_device_image'),
    ]

    operations = [
        migrations.RunPython(create_cache_table, migrations.RunPython.noop),
    ]
