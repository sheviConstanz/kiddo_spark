from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from core.migrations._defense_seed_v1 import KEY, PREFIX, ensure_future_slots
from core.models import Activity, Booking, DemoScenario, Organization, Review, Schedule


class Command(BaseCommand):
    help = 'Extiende 35 días la agenda de la base de defensa sin mover ni reemplazar operaciones.'

    @transaction.atomic
    def handle(self, **options):
        if not getattr(settings, 'KIDDO_DEFENSE_DEMO', False) or not settings.KIDDO_ALLOW_DEMO_DATA:
            raise CommandError('Usa --settings=kiddo.defense_settings; la base normal no se modifica.')
        marker = DemoScenario.objects.filter(key=KEY)
        if not marker.update(key=F('key')):
            raise CommandError('Primero aplica migrate con la configuración de defensa.')
        created = ensure_future_slots(apps, 'default')
        activities = Activity.objects.filter(origin_key__startswith=PREFIX + 'activity:')
        future = Schedule.objects.filter(activity__in=activities, starts_at__gt=timezone.now(), active=True, available__gt=0)
        end = timezone.localtime(future.order_by('-starts_at').first().starts_at).date() if future.exists() else None
        self.stdout.write(self.style.SUCCESS(
            f'Defensa: {Organization.objects.filter(origin_key__startswith=PREFIX, approved=True).count()} proveedores aprobados, '
            f'{activities.count()} actividades, {Booking.objects.filter(schedule__activity__in=activities).count()} reservas, '
            f'{Review.objects.filter(booking__schedule__activity__in=activities).count()} opiniones. '
            f'{created} horarios añadidos; {future.count()} horarios con cupos, hasta {end}.'
        ))
