from django.conf import settings
from django.db import migrations

from ._defense_seed_v1 import populate


def load_defense_data(apps, schema_editor):
    if getattr(settings, 'KIDDO_DEFENSE_DEMO', False) and getattr(settings, 'KIDDO_ALLOW_DEMO_DATA', False):
        populate(apps, schema_editor.connection.alias)


class Migration(migrations.Migration):
    dependencies = [('core', '0012_provider_publications_demo')]
    # The reverse intentionally preserves fictional operations and their history.
    operations = [migrations.RunPython(load_defense_data, migrations.RunPython.noop)]
