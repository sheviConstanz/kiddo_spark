"""Import the reference catalogue without evaluating its JavaScript or overwriting edits."""
import re
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from core.models import User, City, Category, Organization, Activity, Schedule, Plan
from core.relief import REFERENCE_AREAS


def field(text, key):
    match = re.search(r"\b" + key + r":'((?:\\.|[^'])*)'", text)
    if not match:
        raise ValueError('Campo de referencia ausente: ' + key)
    return match[1].replace("\\'", "'")


def number(text, key):
    return int(re.search(r'\b' + key + r':(\d+)', text)[1])


def example_start(period, now):
    """Give newly seeded activities a future slot in their reference period."""
    starts_at = timezone.localtime(now) + timedelta(days=7)
    weekend = period == 'Fin de semana'
    while (starts_at.weekday() >= 5) != weekend:
        starts_at += timedelta(days=1)
    hour = 10 if weekend or period == 'Mañana' else 17
    return starts_at.replace(hour=hour, minute=0, second=0, microsecond=0)


def seeded(model, key, lookup, defaults):
    existing = model.objects.filter(origin_key=key).first()
    if existing:
        return existing, False
    # Backfill imports from earlier schema versions without changing human edits.
    existing = model.objects.filter(origin_key__isnull=True, **lookup).first()
    if existing:
        existing.origin_key = key
        existing.save(update_fields=['origin_key'])
        return existing, False
    return model.objects.create(origin_key=key, **lookup, **defaults), True


class Command(BaseCommand):
    help = 'Carga catálogo y planes de referencia, sin usuarios con contraseña ni sobrescribir registros existentes.'

    def add_arguments(self, parser):
        parser.add_argument('--scenario', action='store_true', help='Añade una sola vez cuentas y operaciones ficticias conectadas, solo en la demo local.')

    @transaction.atomic
    def handle(self, **options):
        if options.get('scenario'):
            from core.demo_scenario import load_scenario
            created = load_scenario()
            self.stdout.write(self.style.SUCCESS(
                'Escenario académico cargado: 4 fichas, 4 familias y 12 reservas ficticias. Accesos y recorrido en docs/DEMO-ACADEMICA.md.'
                if created else 'El escenario ya estaba cargado. Se conservaron las cuentas, fechas, ediciones y operaciones existentes.'
            ))
            return
        source = (settings.BASE_DIR / 'Kiddo Spark B2B2C.html').read_text(encoding='utf-8')
        owner, created = User.objects.get_or_create(username='_catalogo_demo', defaults={'email': 'catalogo@example.invalid', 'is_active': False})
        if created:
            owner.set_unusable_password()
            owner.save()
        group, _ = Group.objects.get_or_create(name='Administradores de organización')
        allowed_models = ['organization', 'activity', 'schedule', 'campaign', 'booking', 'servicerequest', 'review', 'bankaccount', 'withdrawal', 'settlement']
        group.permissions.set(Permission.objects.filter(content_type__app_label='core', content_type__model__in=allowed_models))
        for name, sparks, price, description in [('Explorador', 15, 24990, 'Para probar distintas actividades.'), ('Integral', 26, 34990, 'Equilibrio para combinar disciplinas.'), ('Full Spark', 34, 45499, 'Más actividad y mayor frecuencia.')]:
            seeded(Plan, 'plan:' + name, {'name': name}, {'sparks': sparks, 'price': price, 'description': description})
        raw = source.split('const activities=[', 1)[1].split('\n];', 1)[0]
        price_by_name = {'Natación formativa': 28000, 'Jiu-Jitsu infantil': 23000, 'Robótica STEAM': 25000, 'Danza infantil': 22000, 'Piano inicial': 26000}
        for line in raw.splitlines():
            if not line.strip().startswith('{id:'):
                continue
            city, _ = City.objects.get_or_create(name=field(line, 'city'))
            category, _ = Category.objects.get_or_create(name=field(line, 'cat'))
            org, _ = seeded(Organization, 'provider:' + field(line, 'center'), {'name': field(line, 'center'), 'kind': 'provider'}, {'city': city, 'email': 'centro@example.invalid', 'created_by': owner, 'approved': True, 'description': 'Centro del catálogo de referencia. Datos usados solo para la demostración.'})
            age_min, age_max = map(int, field(line, 'age').split('-'))
            activity, created = seeded(Activity, 'activity:' + str(number(line, 'id')), {'name': field(line, 'name'), 'organization': org}, {'category': category, 'description': field(line, 'desc'), 'age_min': age_min, 'age_max': age_max, 'sparks': number(line, 'sparks'), 'price': price_by_name.get(field(line, 'name'), 0), 'icon': field(line, 'icon')})
            if created:
                start = example_start(field(line, 'time'), timezone.now())
                spots = number(line, 'spots')
                Schedule.objects.create(activity=activity, starts_at=start, capacity=max(1, spots), available=spots)
        default_city = City.objects.get(name='Valparaíso')
        raw = source.split('const allies=[', 1)[1].split('\n];', 1)[0]
        for line in raw.splitlines():
            if line.strip().startswith('{cat:'):
                name = field(line, 'name')
                description = field(line, 'desc')
                if name == 'Espacio Seguro Mantención':
                    description = 'Apoyo de ejemplo para recintos deportivos, artísticos y culturales.'
                tags = re.search(r'tags:\[([^\]]*)\]', line)[1]
                seeded(Organization, 'ally:' + name, {'name': name, 'kind': 'ally'}, {
                    'city': default_city, 'email': 'aliado@example.invalid', 'created_by': owner,
                    'approved': True, 'description': description,
                    'relief_area': REFERENCE_AREAS[field(line, 'cat')],
                    'relief_focus': field(line, 'meta'),
                    'relief_topics': '; '.join(re.findall(r"'([^']+)'", tags)),
                })
        self.stdout.write(self.style.SUCCESS('Catálogo de referencia, planes y grupo administrador preparados. No se crearon contraseñas. Repetir no sobrescribe registros existentes.'))
