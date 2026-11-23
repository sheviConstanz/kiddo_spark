"""Opt-in fictional presentation records; never overwrite existing accounts."""
from datetime import timedelta

from django.conf import settings
from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone

from . import models as m, services


SCENARIO_KEY = 'academic-presentation-2026-v1'
DEMO_PASSWORD = 'DemoAcademica2026!'


def new_account(username, *, applicant=False):
    email = f'{username}@presentation.example.invalid'
    if m.User.objects.filter(username=username).exists() or m.User.objects.filter(email__iexact=email).exists():
        raise CommandError(f'La cuenta {username} ya existe. No se modificó. Usa una base de demostración separada.')
    return m.User.objects.create_user(
        username, email=email, password=DEMO_PASSWORD, provider_applicant=applicant,
        first_name='Persona ficticia', last_name='Demostración',
    )


def stamp_booking(booking, date):
    m.Booking.objects.filter(pk=booking.pk).update(created_at=date)
    m.Movement.objects.filter(booking=booking).update(created_at=date)
    m.Notification.objects.filter(booking=booking).update(created_at=date)


@transaction.atomic
def load_scenario():
    if not getattr(settings, 'KIDDO_ALLOW_DEMO_DATA', False) or not settings.KIDDO_SEED_DEMO_ACCOUNTS:
        raise CommandError('La carga de escenarios y cuentas ficticias solo está habilitada en la demo local.')
    _, created = m.DemoScenario.objects.get_or_create(key=SCENARIO_KEY)
    if not created:
        return False
    actor = m.User.objects.filter(is_superuser=True, is_active=True).first()
    if actor is None:
        raise CommandError('Primero prepara las cuentas de la demo local con migrate.')
    now = timezone.now()
    families = [new_account(f'familia_demo_{index:03}') for index in range(1, 5)]
    plan = m.Plan.objects.create(
        origin_key='scenario:credits', name='Créditos de prueba académica', sparks=80, price=0,
        description='Recarga de crédito simulado. Sin pago y sin conversión Spark/CLP.',
    )
    for family in families:
        membership = services.activate_plan(family, plan)
        m.Membership.objects.filter(pk=membership.pk).update(created_at=now - timedelta(days=25))
        m.Movement.objects.filter(membership=membership).update(created_at=now - timedelta(days=25))

    centers = []
    for index, (username, name, city_name, category_name, status) in enumerate((
        ('kidsdemo', 'Kids Demo', 'Viña del Mar', 'Apoyo escolar', 'approved'),
        ('robotica_demo', 'Robótica Demo', 'Valparaíso', 'Tecnología', 'approved'),
        ('deporte_demo', 'Deporte Demo', 'Quilpué', 'Deportes', 'pending'),
        ('arte_demo', 'Arte Demo', 'Villa Alemana', 'Arte', 'observed'),
    )):
        owner = new_account(username, applicant=True)
        city, _ = m.City.objects.get_or_create(name=city_name)
        category, _ = m.Category.objects.get_or_create(name=category_name)
        center = m.Organization.objects.create(
            origin_key=f'scenario:center:{index}', name=name, city=city, specialty=category,
            email=owner.email, created_by=owner, description='Centro ficticio para demostración académica.',
            contact_first_name='Contacto', contact_last_name='Ficticio', phone='Sin teléfono real',
        )
        m.ProviderReviewEvent.objects.create(organization=center, actor=owner, status='pending', note='Solicitud de demostración.')
        if status != 'pending':
            services.review_provider(actor, center, center.review_events.first().pk, 'reviewing', 'Revisión de datos ficticios.')
            services.review_provider(actor, center, center.review_events.first().pk, status,
                                     'Ficha ficticia aprobada.' if status == 'approved' else 'Completar la descripción del taller de ejemplo.')
        if status == 'approved':
            center.refresh_from_db()
            owner.refresh_from_db()
            centers.append((owner, center))

    for index, (owner, center) in enumerate(centers):
        title = 'Matemáticas básicas' if index == 0 else 'Robótica creativa demo'
        activity = m.Activity.objects.create(
            origin_key=f'scenario:activity:{index}', name=title, organization=center, category=center.specialty,
            description='Actividad de demostración; no corresponde a un servicio comercial real.',
            age_min=5, age_max=14, sparks=4, price=25000, demo_data=True,
            venue=f'Sala ficticia en {center.city.name}', publication_status='published',
        )
        for state, label in (('draft', 'en preparación'), ('paused', 'en pausa')):
            m.Activity.objects.create(
                origin_key=f'scenario:activity:{index}:{state}', name=f'{title} · {label}', organization=center,
                category=center.specialty, description='Ficha ficticia fuera del catálogo familiar.', demo_data=True,
                active=False, publication_status=state, venue='Sala ficticia',
            )
        future = m.Schedule.objects.create(activity=activity, starts_at=now + timedelta(days=7 + index, hours=2), capacity=10, available=10)
        m.Schedule.objects.create(activity=activity, starts_at=now + timedelta(days=14 + index), capacity=8, available=8)
        for number, family in enumerate(families):
            booking = services.reserve(family, future.pk)
            if number == 3:
                services.cancel(family, booking)
            stamp_booking(booking, now - timedelta(days=number))

        # Construct a labeled historical fixture through the same balance/capacity services.
        past = m.Schedule.objects.create(activity=activity, starts_at=now + timedelta(days=1), capacity=6, available=6)
        for number, family in enumerate(families[:2]):
            booking = services.reserve(family, past.pk)
            services.complete(owner, booking)
            stamp_booking(booking, now - timedelta(days=15 + number))
            review = m.Review.objects.create(
                booking=booking, rating=4 + number, comment='Opinión ficticia para la demostración académica.', is_demo=True,
            )
            m.Review.objects.filter(pk=review.pk).update(created_at=now - timedelta(days=9))
        m.Schedule.objects.filter(pk=past.pk).update(starts_at=now - timedelta(days=10))
    return True
