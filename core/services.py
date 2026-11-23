from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone
from .access import may_reserve, may_review_providers, operates_platform, schedule_cancellation_centers
from .models import User, Schedule, Booking, Membership, Movement, Notification, Organization, Settlement, Withdrawal, RequestEvent, AuditLog, ProviderReviewEvent


def audit(user, action, obj):
    AuditLog.objects.create(actor=user, action=action, target=f'{obj._meta.model_name}:{obj.pk}')


@transaction.atomic
def submit_request(user, service_request):
    service_request.user = user
    service_request.save()
    RequestEvent.objects.create(
        request=service_request, actor=user, status='pending', note='Solicitud recibida en la plataforma.',
    )
    audit(user, 'request_create', service_request)


ProviderStatus = ProviderReviewEvent.Status
PROVIDER_DECISIONS = {
    ProviderStatus.PENDING: (ProviderStatus.REVIEWING,),
    ProviderStatus.REVIEWING: (ProviderStatus.APPROVED, ProviderStatus.OBSERVED, ProviderStatus.REJECTED),
}


def provider_status(organization, latest):
    if organization.approved:
        return ProviderStatus.APPROVED
    return ProviderStatus(latest.status) if latest else ProviderStatus.PENDING


def enable_provider(organization):
    """Grant only organization-scoped operator capabilities to the applicant."""
    owner = User.objects.get(pk=organization.created_by_id)
    if not owner.is_active or operates_platform(owner):
        return
    permissions = {
        'organization': ('view', 'change'),
        'activity': ('view', 'add', 'change', 'delete'),
        'schedule': ('view', 'add', 'change'),
        'booking': ('view', 'change'),
        'servicerequest': ('view', 'change'),
        'review': ('view', 'change'),
        'campaign': ('view', 'add', 'change', 'delete'),
        'settlement': ('view',), 'withdrawal': ('view', 'add'),
        'bankaccount': ('view', 'add', 'change'),
    }
    group, _ = Group.objects.get_or_create(name='Operadores de proveedor')
    codenames = [f'{action}_{model}' for model, actions in permissions.items() for action in actions]
    group.permissions.set(Permission.objects.filter(content_type__app_label='core', codename__in=codenames))
    owner.is_staff = True
    owner.provider_applicant = False
    owner.save(update_fields=['is_staff', 'provider_applicant'])
    owner.groups.add(group)
    organization.administrators.add(owner)


@transaction.atomic
def enable_approved_provider(actor, organization):
    if not may_review_providers(actor):
        raise PermissionDenied
    current = Organization.objects.filter(pk=organization.pk, kind='provider', approved=True, active=True)
    if not current.update(approved=F('approved')):
        raise ValidationError('La ficha debe estar aprobada y vigente.')
    center = current.get()
    if not center.created_by.is_active:
        raise ValidationError('La cuenta titular está desactivada. Superadministración debe revisar su acceso.')
    if center.administrators.filter(pk=center.created_by_id, is_staff=True).exists() and center.created_by.has_perm('core.add_activity'):
        return
    enable_provider(center)
    audit(actor, 'provider_enabled', center)


def lock_provider_revision(organization, revision, **scope):
    # Acquire a SQLite write lock before reading the current event or state.
    candidates = Organization.objects.filter(pk=organization.pk, kind='provider', approved=False, **scope)
    if not candidates.update(approved=F('approved')):
        raise ValidationError('La ficha ya no admite esta acción. Vuelve a consultar su estado.')
    current = candidates.get()
    latest = current.review_events.first()
    if revision != (latest.pk if latest else 0):
        raise ValidationError('La ficha cambió mientras estaba abierta. Revisa el historial antes de continuar.')
    return current, latest


@transaction.atomic
def review_provider(actor, organization, revision, status, note):
    if not may_review_providers(actor):
        raise PermissionDenied('Esta cuenta no puede resolver solicitudes de proveedores.')
    current, latest = lock_provider_revision(organization, revision, active=True)
    if status not in PROVIDER_DECISIONS.get(provider_status(current, latest), ()) or not note.strip():
        raise ValidationError('Selecciona una decisión válida y escribe el motivo.')
    if status == ProviderStatus.APPROVED:
        current.approved = True
        current.save(update_fields=['approved'])
        enable_provider(current)
    ProviderReviewEvent.objects.create(organization=current, actor=actor, status=status, note=note)
    audit(actor, 'provider_' + status, current)


@transaction.atomic
def resubmit_provider(actor, organization, revision, updates):
    current, latest = lock_provider_revision(organization, revision, created_by=actor, active=True)
    if provider_status(current, latest) != ProviderStatus.OBSERVED:
        raise ValidationError('Solo se puede reenviar una ficha que requiere corrección.')
    for field, value in updates.items():
        setattr(current, field, value)
    current.save(update_fields=updates.keys())
    ProviderReviewEvent.objects.create(
        organization=current, actor=actor, status=ProviderStatus.PENDING,
        note='El solicitante corrigió y reenvió la ficha.',
    )


@transaction.atomic
def activate_plan(user, plan):
    if not plan.active:
        raise ValidationError('Este plan ya no está disponible.')
    membership = Membership.objects.create(user=user, plan=plan, sparks=plan.sparks)
    User.objects.filter(pk=user.pk).update(credits=F('credits') + plan.sparks)
    Movement.objects.create(user=user, delta=plan.sparks, description=f'Activación demo: {plan.name}', membership=membership)
    audit(user, 'activate_plan', membership)
    return membership


def bookable_schedules():
    return Schedule.objects.filter(
        active=True, starts_at__gt=timezone.now(), activity__active=True,
        activity__publication_status='published',
        activity__organization__active=True, activity__organization__approved=True,
        activity__organization__kind='provider',
    )


def schedule_cancellation_cutoff(now):
    return now + timedelta(hours=48)


def booking_message(booking, detail):
    start = timezone.localtime(booking.schedule.starts_at)
    return f'{booking.schedule.activity.name} · {start:%d/%m/%Y %H:%M}. {detail}'


def notify_booking(booking, kind, detail):
    Notification.objects.create(
        recipient_id=booking.user_id, booking=booking, kind=kind,
        message=booking_message(booking, detail),
    )


@transaction.atomic
def reserve(user, schedule_id):
    if not may_reserve(user):
        raise PermissionDenied('Este perfil no puede crear reservas.')
    # Conditional writes also serialize competing SQLite writers before reading balances.
    if not bookable_schedules().filter(pk=schedule_id, available__gt=0).update(available=F('available') - 1):
        raise ValidationError('El horario no está disponible o no tiene cupos.')
    slot = Schedule.objects.select_related('activity').get(pk=schedule_id)
    if Booking.objects.filter(user=user, schedule=slot, status=Booking.Status.RESERVED).exists():
        raise ValidationError('Ya tienes una reserva para este horario.')
    if not User.objects.filter(pk=user.pk, credits__gte=slot.activity.sparks).update(credits=F('credits') - slot.activity.sparks):
        raise ValidationError('No tienes suficientes Sparks. Activa un plan de demostración.')
    booking = Booking.objects.create(user=user, schedule=slot, sparks=slot.activity.sparks, amount=slot.activity.price)
    Movement.objects.create(user=user, delta=-booking.sparks, description='Reserva de actividad', booking=booking)
    notify_booking(booking, Notification.Kind.RESERVED, f'Se descontaron {booking.sparks} Sparks.')
    operators = slot.activity.organization.administrators.filter(is_active=True, is_staff=True).exclude(pk=user.pk)
    notice = booking_message(booking, f'La reserva KS-{booking.pk} ya está confirmada.')
    Notification.objects.bulk_create([
        Notification(recipient=operator, booking=booking, kind=Notification.Kind.BOOKING_RECEIVED, message=notice)
        for operator in operators if operator.role == 'provider' and operator.has_perm('core.view_booking')
    ])
    audit(user, 'reserve', booking)
    return booking


def _refund_booking(booking):
    current = Booking.objects.filter(pk=booking.pk, status=Booking.Status.RESERVED, attendance_recorded=False)
    if not current.update(status=Booking.Status.CANCELLED):
        raise ValidationError('La reserva ya fue cancelada o tiene asistencia registrada.')
    Schedule.objects.filter(pk=booking.schedule_id).update(available=F('available') + 1)
    refund = {'credits': F('credits') + booking.sparks}
    if Booking.objects.filter(pk=booking.pk, points_awarded=True).update(points_awarded=False):
        refund['points'] = F('points') - 50
    User.objects.filter(pk=booking.user_id).update(**refund)
    Movement.objects.create(user_id=booking.user_id, delta=booking.sparks, description='Devolución por cancelación', booking=booking)


@transaction.atomic
def cancel(user, booking):
    if booking.user_id != user.pk:
        raise ValidationError('Solo el titular puede cancelar su reserva.')
    _refund_booking(booking)
    notify_booking(booking, Notification.Kind.BOOKING_CANCELLED, f'Se devolvieron {booking.sparks} Sparks a tu cuenta.')
    audit(user, 'cancel', booking)


def cancel_schedule(user, schedule, reason):
    centers = schedule_cancellation_centers(user)
    if not centers.filter(pk=schedule.activity.organization_id).exists():
        raise PermissionDenied
    reason = reason.strip()
    if not reason or len(reason) > 500:
        raise ValidationError('Escribe un motivo de hasta 500 caracteres.')

    now = timezone.now()
    with transaction.atomic():
        # Update the same slot that reserve() locks before debiting the client.
        eligible = Schedule.objects.filter(
            pk=schedule.pk, active=True, cancelled_at__isnull=True,
            starts_at__gte=schedule_cancellation_cutoff(now), activity__organization__in=centers,
        )
        if not eligible.update(active=False, cancelled_at=now, cancellation_reason=reason):
            raise ValidationError('Solo puedes cancelar un horario activo con al menos 48 horas de anticipación.')
        bookings = Booking.objects.filter(
            schedule=schedule, status=Booking.Status.RESERVED, attendance_recorded=False,
        ).select_related('schedule__activity')
        for booking in bookings:
            _refund_booking(booking)
            notify_booking(
                booking, Notification.Kind.SCHEDULE_CANCELLED,
                f'Motivo: {reason}\nSe devolvieron {booking.sparks} Sparks a tu cuenta.',
            )
        audit(user, 'cancel_schedule', schedule)


@transaction.atomic
def complete(user, booking):
    current = Booking.objects.filter(pk=booking.pk)
    if not current.filter(status=Booking.Status.RESERVED, attendance_recorded=False).update(attendance_recorded=True):
        raise ValidationError('Solo puedes registrar asistencia una vez en una reserva vigente.')
    Settlement.objects.create(booking=booking, organization=booking.schedule.activity.organization, amount=booking.amount)
    if current.filter(points_awarded=False).update(points_awarded=True):
        User.objects.filter(pk=booking.user_id).update(points=F('points') + 50)
    audit(user, 'complete', booking)


def available_balance(org):
    income = Settlement.objects.filter(organization=org).aggregate(n=Sum('amount'))['n'] or 0
    reserved = Withdrawal.objects.filter(organization=org, status__in=['pending', 'paid']).aggregate(n=Sum('amount'))['n'] or 0
    return income - reserved


@transaction.atomic
def withdraw(user, org, amount):
    Organization.objects.filter(pk=org.pk).update(active=F('active'))
    if amount <= 0 or amount > available_balance(org):
        raise ValidationError('El monto debe ser positivo y no superar el saldo disponible demo.')
    obj = Withdrawal.objects.create(user=user, organization=org, amount=amount)
    audit(user, 'withdraw_demo', obj)
    return obj


@transaction.atomic
def transition_request(user, obj, status, note):
    allowed = {'pending': {'reviewing', 'rejected'}, 'reviewing': {'approved', 'rejected'}, 'approved': {'completed'}, 'rejected': set(), 'completed': set()}
    current = type(obj).objects.select_for_update().get(pk=obj.pk)
    if status not in allowed[current.status]:
        raise ValidationError('La transición de estado no es válida.')
    current.status = status
    current.save(update_fields=['status'])
    RequestEvent.objects.create(request=current, actor=user, status=status, note=note)
    audit(user, 'request_status', current)
