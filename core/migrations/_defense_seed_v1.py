"""Frozen historical-model fixture for migration 0013; no runtime model imports."""
from datetime import datetime, time, timedelta

from django.contrib.auth.hashers import make_password
from django.utils import timezone


KEY = 'defense-v1'
PREFIX = 'defense:v1:'
PASSWORD = 'DemoAcademica2026!'
CITIES = ('Viña del Mar', 'Valparaíso', 'Quilpué', 'Villa Alemana')
PROVIDERS = (
    'Academia Horizonte', 'Taller Puerto Creativo', 'Club Marga Marga',
    'Escuela Pequeños Exploradores', 'Centro Brisa Marina', 'Aula Cerro Alegre',
    'Espacio Recreo Quilpué', 'Academia Sol del Valle',
)
# provider, title, category, minimum age, maximum age, Sparks, independent CLP reference
ACTIVITIES = (
    (0, 'Natación infantil', 'Deportes', 5, 9, 5, 28000),
    (0, 'Jiu-Jitsu infantil', 'Deportes', 8, 14, 4, 23000),
    (0, 'Danza creativa', 'Arte', 5, 10, 3, 22000),
    (0, 'Robótica STEAM', 'Tecnología', 9, 14, 6, 32000),
    (1, 'Pintura y color', 'Arte', 5, 9, 3, 18000),
    (1, 'Teatro y expresión', 'Arte', 8, 14, 4, 24000),
    (1, 'Piano inicial', 'Música', 7, 12, 6, 30000),
    (2, 'Fútbol formativo', 'Deportes', 7, 12, 4, 22000),
    (2, 'Básquetbol infantil', 'Deportes', 9, 14, 4, 24000),
    (2, 'Atletismo y juegos', 'Deportes', 5, 10, 3, 19000),
    (3, 'Ciencia entretenida', 'Ciencias', 8, 13, 5, 26000),
    (3, 'Ajedrez para explorar', 'Recreación', 7, 14, 3, 18000),
    (4, 'Yoga y movimiento', 'Recreación', 5, 10, 3, 20000),
    (4, 'Percusión en equipo', 'Música', 8, 14, 5, 25000),
    (5, 'Matemáticas con juegos', 'Apoyo escolar', 7, 11, 4, 24000),
    (5, 'Lectura y cuentos', 'Apoyo escolar', 5, 8, 3, 18000),
    (6, 'Patinaje inicial', 'Deportes', 6, 12, 5, 27000),
    (6, 'Huerto y naturaleza', 'Recreación', 5, 11, 4, 21000),
    (7, 'Programación creativa', 'Tecnología', 10, 14, 6, 30000),
    (7, 'Inglés en acción', 'Apoyo escolar', 8, 13, 4, 25000),
)
COMMENTS = (
    'Las instrucciones fueron claras y el grupo tuvo buen acompañamiento.',
    'Buena experiencia de prueba; nos gustaría una explicación inicial más larga.',
    'El taller combinó práctica y juegos de manera entretenida.',
    'La actividad cumplió lo esperado. Mejoraría la organización de la llegada.',
    'Nos gustó la variedad de ejercicios y el trato del equipo.',
)


def at(day, hour=17):
    return timezone.make_aware(datetime.combine(day, time(hour)), timezone.get_default_timezone())


def ensure_future_slots(apps, database, now=None):
    today = timezone.localtime(now or timezone.now()).date()
    slots = apps.get_model('core', 'Schedule').objects.using(database)
    activities = apps.get_model('core', 'Activity').objects.using(database).filter(
        origin_key__startswith=PREFIX + 'activity:', active=True, publication_status='published',
        organization__active=True, organization__approved=True,
    )
    count = 0
    for activity in activities:
        index = int(activity.origin_key.rsplit(':', 1)[1])
        weekdays = {(index + shift) % 7 for shift in (1, 3, 5)}
        for offset in range(1, 36):
            day = today + timedelta(days=offset)
            if day.weekday() not in weekdays:
                continue
            hour = 10 + index % 2 if day.weekday() >= 5 else (10 if index % 3 == 0 else 16 + index % 3)
            _, created = slots.get_or_create(
                activity_id=activity.pk, starts_at=at(day, hour),
                defaults={'capacity': 4 + index % 5 * 2, 'available': 4 + index % 5 * 2, 'active': True},
            )
            count += created
    return count


def populate(apps, database, now=None):
    now = now or timezone.now()
    today = timezone.localtime(now).date()
    models = {name: apps.get_model('core', name) for name in (
        'User', 'Organization', 'City', 'Category', 'ProviderReviewEvent', 'Activity', 'Schedule',
        'Plan', 'Membership', 'Booking', 'Movement', 'Review', 'Settlement', 'Notification',
        'Favorite', 'AuditLog', 'ServiceRequest', 'RequestEvent', 'DemoScenario',
    )}

    def objects(name):
        return models[name].objects.using(database)

    marker, created = objects('DemoScenario').get_or_create(key=KEY)
    if not created:
        return False
    # Abort, rather than re-use or overwrite any pre-existing account.
    usernames = ['defensa_admin', 'defensa_superadmin'] + [f'defensa_proveedor_{i:02}' for i in range(1, 12)] + [f'defensa_familia_{i:02}' for i in range(1, 31)]
    if objects('User').filter(username__in=usernames).exists() or objects('User').filter(email__endswith='@defense.example.invalid').exists():
        raise ValueError('La base contiene cuentas anteriores. Prepara una base de defensa nueva, sin reemplazarlas.')
    password = make_password(PASSWORD)

    def account(username, staff=False, root=False, applicant=False):
        return objects('User').create(
            username=username, email=f'{username}@defense.example.invalid', password=password,
            first_name='Familia ficticia' if 'familia' in username else 'Operador ficticio',
            last_name=username.rsplit('_', 1)[-1] if '_' in username else 'Defensa',
            is_active=True, is_staff=staff, is_superuser=root, provider_applicant=applicant,
            date_joined=now - timedelta(days=120),
        )

    def record(model_name, when, **values):
        obj = objects(model_name).create(**values)
        objects(model_name).filter(pk=obj.pk).update(created_at=when)
        return obj

    def permission(user, model, actions):
        content, _ = apps.get_model('contenttypes', 'ContentType').objects.using(database).get_or_create(app_label='core', model=model)
        for action in actions:
            codename = f'{action}_{model}' if action != 'operate_platform' else action
            perm, _ = apps.get_model('auth', 'Permission').objects.using(database).get_or_create(
                content_type=content, codename=codename, defaults={'name': f'Demo {codename}'},
            )
            user.user_permissions.add(perm)

    admin = account('defensa_admin', staff=True)
    account('defensa_superadmin', staff=True, root=True)
    permission(admin, 'user', ('operate_platform',))
    for model in ('activity', 'schedule', 'category', 'city', 'plan'):
        permission(admin, model, ('view', 'add', 'change', 'delete'))
    for model in ('booking', 'servicerequest', 'review'):
        permission(admin, model, ('view', 'change'))
    permission(admin, 'organization', ('view',))

    cities = [objects('City').get_or_create(name=name)[0] for name in CITIES]
    categories = {name: objects('Category').get_or_create(name=name)[0] for name in {row[2] for row in ACTIVITIES}}
    centers, owners = [], []
    for index in range(11):
        approved = index < 8
        owner = account(f'defensa_proveedor_{index + 1:02}', staff=approved, applicant=not approved)
        center = objects('Organization').create(
            origin_key=f'{PREFIX}center:{index:02}', name=(PROVIDERS[index] if approved else f'Centro en incorporación {index - 7}') + ' · Demo',
            city=cities[index % 4], specialty=categories['Deportes' if index % 2 == 0 else 'Arte'],
            created_by_id=owner.pk, email=owner.email, approved=approved, active=True,
            description='Centro ficticio de la base de defensa. Sin servicios ni cobros reales.',
            contact_first_name='Contacto', contact_last_name='Ficticio', phone='Sin teléfono real',
        )
        submitted = now - timedelta(days=110 if approved else 5)
        record('ProviderReviewEvent', submitted, organization_id=center.pk, actor_id=owner.pk, status='pending', note='Ficha ficticia recibida.')
        if index != 8:
            record('ProviderReviewEvent', submitted + timedelta(days=1), organization_id=center.pk, actor_id=admin.pk, status='reviewing', note='Revisión académica de datos ficticios.')
        if approved or index == 10:
            record('ProviderReviewEvent', submitted + timedelta(days=2), organization_id=center.pk, actor_id=admin.pk,
                   status='approved' if approved else 'observed', note='Aprobación demo.' if approved else 'Completar la descripción del centro de ejemplo.')
        if approved:
            center.administrators.add(owner)
            for model in ('organization', 'activity', 'schedule', 'booking', 'servicerequest', 'review', 'campaign'):
                permission(owner, model, ('view', 'change') if model in ('organization', 'booking', 'servicerequest', 'review') else ('view', 'add', 'change', 'delete'))
            permission(owner, 'settlement', ('view',))
        centers.append(center)
        owners.append(owner)

    plan = objects('Plan').create(origin_key=PREFIX + 'credits', name='Recarga de defensa · Demo', sparks=100, price=0, description='100 créditos simulados, sin conversión Spark/CLP ni pago.')
    families = [account(f'defensa_familia_{index:02}') for index in range(1, 31)]
    for family in families:
        family.credits = 100
        membership = record('Membership', now - timedelta(days=110), user_id=family.pk, plan_id=plan.pk, sparks=100)
        record('Movement', now - timedelta(days=110), user_id=family.pk, delta=100, description='Recarga de crédito simulado · Defensa', membership_id=membership.pk)

    activities = []
    for index, (provider, title, category, lower, upper, sparks, price) in enumerate(ACTIVITIES):
        activity = record('Activity', now - timedelta(days=100), origin_key=f'{PREFIX}activity:{index:02}',
            organization_id=centers[provider].pk, name=title + ' · Demo', category_id=categories[category].pk,
            description=f'Taller ficticio de {title.lower()} con actividades guiadas y grupos por edad. Datos de demostración.',
            age_min=lower, age_max=upper, sparks=sparks, price=price, active=True, publication_status='published',
            modality='in_person', venue=f'Sala ficticia de {centers[provider].name}, {centers[provider].city.name}',
            demo_data=True, icon=('🏊', '🥋', '🎨', '🤖', '🎭')[index % 5],
        )
        activities.append(activity)
    ensure_future_slots(apps, database, now)

    counter, opinions = 0, 0
    for index, activity in enumerate(activities):
        count = (12, 8, 5, 3)[index] if index < 4 else 2
        provider = ACTIVITIES[index][0]
        for number in range(count):
            kind = 'completed' if number == 0 else 'future' if number == 1 else ('completed', 'customer_cancel', 'unrecorded', 'center_cancel', 'future')[(number - 2) % 5]
            family = families[0] if index == 0 and number == 1 else families[counter % 30]
            if kind == 'future':
                slot = objects('Schedule').filter(activity_id=activity.pk, starts_at__gt=now, active=True, available__gt=0).order_by('starts_at').first()
                reserved_at = now - timedelta(days=number % 4, hours=1)
            else:
                ago = (75, 60, 45, 30, 20, 10)[(index + number) % 6]
                starts = at(today - timedelta(days=ago + number // 6), 10 + index % 8)
                slot, _ = objects('Schedule').get_or_create(activity_id=activity.pk, starts_at=starts,
                    defaults={'capacity': 12, 'available': 12, 'active': True})
                reserved_at = starts - timedelta(days=7)
            cancelled = kind in ('customer_cancel', 'center_cancel')
            attended = kind == 'completed'
            booking = record('Booking', reserved_at, user_id=family.pk, schedule_id=slot.pk,
                sparks=activity.sparks, amount=activity.price, status='cancelled' if cancelled else 'reserved',
                attendance_recorded=attended, points_awarded=attended)
            record('Movement', reserved_at, user_id=family.pk, delta=-activity.sparks, booking_id=booking.pk, description='Reserva con crédito simulado · Defensa')
            record('AuditLog', reserved_at, actor_id=family.pk, action='reserve', target=f'booking:{booking.pk}')
            for recipient, notification_kind in ((family.pk, 'reserved'), (owners[provider].pk, 'booking_received')):
                record('Notification', reserved_at, recipient_id=recipient, booking_id=booking.pk, kind=notification_kind,
                    message=f'Demostración: KS-{booking.pk} · {activity.name} · {timezone.localtime(slot.starts_at):%d/%m/%Y %H:%M}.')
            if cancelled:
                cancelled_at = slot.starts_at - timedelta(days=3)
                record('Movement', cancelled_at, user_id=family.pk, delta=activity.sparks, booking_id=booking.pk, description='Devolución de crédito simulado · Defensa')
                record('Notification', cancelled_at, recipient_id=family.pk, booking_id=booking.pk,
                    kind='schedule_cancelled' if kind == 'center_cancel' else 'booking_cancelled',
                    message='Cancelación de demostración. Motivo: ajuste del taller ficticio. Sparks devueltos.')
                if kind == 'center_cancel':
                    objects('Schedule').filter(pk=slot.pk).update(active=False, cancelled_at=cancelled_at, cancellation_reason='Ajuste del taller ficticio · Demostración')
                record('AuditLog', cancelled_at, actor_id=owners[provider].pk if kind == 'center_cancel' else family.pk,
                    action='cancel_schedule' if kind == 'center_cancel' else 'cancel', target=f'{"schedule" if kind == "center_cancel" else "booking"}:{slot.pk if kind == "center_cancel" else booking.pk}')
            else:
                if slot.available <= 0:
                    raise ValueError('La fixture excede la capacidad de una sesión.')
                objects('Schedule').filter(pk=slot.pk).update(available=slot.available - 1)
                family.credits -= activity.sparks
            if attended:
                family.points += 50
                completed_at = slot.starts_at + timedelta(hours=1)
                record('Settlement', completed_at, booking_id=booking.pk, organization_id=activity.organization_id, amount=booking.amount)
                record('AuditLog', completed_at, actor_id=owners[provider].pk, action='complete', target=f'booking:{booking.pk}')
                if opinions < 15:
                    record('Review', completed_at + timedelta(days=1), booking_id=booking.pk, rating=3 + opinions % 3,
                        comment=COMMENTS[opinions % len(COMMENTS)], is_demo=True,
                        response='Gracias por esta opinión de demostración.' if opinions % 2 else '')
                    opinions += 1
            counter += 1
    for family in families:
        if family.credits < 0:
            raise ValueError('Saldo negativo en la fixture de defensa.')
        objects('User').filter(pk=family.pk).update(credits=family.credits, points=family.points)
    for index, activity in enumerate(activities):
        objects('Favorite').get_or_create(user_id=families[index % 30].pk, activity_id=activity.pk)
    for activity in (activities[0], activities[3], activities[14]):
        objects('Favorite').get_or_create(user_id=families[0].pk, activity_id=activity.pk)

    for index, status in enumerate(('pending', 'pending', 'pending', 'reviewing', 'approved', 'completed')):
        when = now - timedelta(days=8 - index)
        request = record('ServiceRequest', when, user_id=owners[index].pk, kind='diagnosis', entity_name=centers[index].name,
            contact_name='Contacto ficticio', contact_email=owners[index].email, subject=('Orientación de seguridad', 'Apoyo contable', 'Orientación comercial')[index % 3] + ' · Demo',
            message='Solicitud ficticia para supervisar el seguimiento B2B de la demostración.', status=status,
            relief_topic='orientation', relief_channel='video', preferred_city_id=centers[index].city_id,
            preferred_date=today + timedelta(days=5 + index) if status != 'completed' else None)
        for step, stage in enumerate(('pending',) if status == 'pending' else ('pending', 'reviewing') if status == 'reviewing' else ('pending', 'reviewing', status)):
            record('RequestEvent', when + timedelta(hours=step), request_id=request.pk, actor_id=owners[index].pk if step == 0 else admin.pk,
                status=stage, note='Seguimiento ficticio; sin contacto ni cita externa.')
    return True
