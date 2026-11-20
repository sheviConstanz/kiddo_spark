from django.conf import settings
from django.db import migrations, models


def preserve_existing_provider_applications(apps, schema_editor):
    database = schema_editor.connection.alias
    organization = apps.get_model('core', 'Organization')
    user = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    applicants = organization.objects.using(database).filter(kind='provider').values('created_by_id')
    user.objects.using(database).filter(
        pk__in=applicants, is_staff=False, is_superuser=False,
    ).update(provider_applicant=True)


class Migration(migrations.Migration):
    dependencies = [('core', '0007_alivios_b2b')]

    operations = [
        migrations.AddField(
            model_name='user',
            name='provider_applicant',
            field=models.BooleanField(default=False, editable=False, verbose_name='solicitante de alta de proveedor'),
        ),
        migrations.RunPython(preserve_existing_provider_applications, migrations.RunPython.noop),
    ]
