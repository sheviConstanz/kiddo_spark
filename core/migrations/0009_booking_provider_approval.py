from django.db import migrations, models


def preserve_previously_awarded_points(apps, schema_editor):
    database = schema_editor.connection.alias
    booking = apps.get_model('core', 'Booking')
    movement = apps.get_model('core', 'Movement')
    debits = movement.objects.using(database).filter(booking_id=models.OuterRef('pk'), delta__lt=0)
    booking.objects.using(database).filter(
        models.Exists(debits),
        status__in=('confirmed', 'completed'),
    ).update(points_awarded=True)


class Migration(migrations.Migration):
    dependencies = [('core', '0008_provider_applicant')]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='points_awarded',
            field=models.BooleanField(default=False, editable=False, verbose_name='puntos acreditados'),
        ),
        migrations.RunPython(preserve_previously_awarded_points, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pendiente de aprobar'), ('confirmed', 'Confirmada'),
                         ('completed', 'Completada'), ('cancelled', 'Cancelada')],
                default='pending',
                max_length=12,
            ),
        ),
        migrations.RemoveConstraint(model_name='booking', name='one_active_booking'),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.UniqueConstraint(
                fields=('user', 'schedule'), condition=models.Q(status__in=('pending', 'confirmed')),
                name='one_active_booking',
            ),
        ),
    ]
