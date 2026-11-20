from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone
from .models import User, Schedule, Booking, Membership, Movement, Organization, Settlement, Withdrawal, RequestEvent, AuditLog, ProviderReviewEvent


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
    if not actor.is_superuser:
        raise ValidationError('Solo superadministración puede resolver la revisión.')
    current, latest = lock_provider_revision(organization, revision, active=True)
    if status not in PROVIDER_DECISIONS.get(provider_status(current, latest), ()) or not note.strip():
        raise ValidationError('Selecciona una decisión válida y escribe el motivo.')
    if status == ProviderStatus.APPROVED:
        current.approved = True
        current.save(update_fields=['approved'])
    ProviderReviewEvent.objects.create(organization=current, actor=actor, status=status, note=note)


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


@transaction.atomic
def reserve(user, schedule_id):
    # Conditional writes also serialize competing SQLite writers before reading balances.
    if not Schedule.objects.filter(pk=schedule_id, active=True, available__gt=0, starts_at__gt=timezone.now(), activity__active=True, activity__organization__active=True, activity__organization__approved=True, activity__organization__kind='provider').update(available=F('available') - 1):
        raise ValidationError('El horario no está disponible o no tiene cupos.')
    slot = Schedule.objects.select_related('activity').get(pk=schedule_id)
    if Booking.objects.filter(user=user, schedule=slot, status='confirmed').exists():
        raise ValidationError('Ya tienes una reserva confirmada para este horario.')
    if not User.objects.filter(pk=user.pk, credits__gte=slot.activity.sparks).update(credits=F('credits') - slot.activity.sparks, points=F('points') + 50):
        raise ValidationError('No tienes suficientes Sparks. Activa un plan de demostración.')
    booking = Booking.objects.create(user=user, schedule=slot, sparks=slot.activity.sparks, amount=slot.activity.price)
    Movement.objects.create(user=user, delta=-booking.sparks, description='Reserva de actividad', booking=booking)
    audit(user, 'reserve', booking)
    return booking


@transaction.atomic
def cancel(user, booking):
    if booking.user_id != user.pk:
        raise ValidationError('Solo el titular puede cancelar su reserva.')
    if not Booking.objects.filter(pk=booking.pk, user=user, status='confirmed').update(status='cancelled'):
        raise ValidationError('La reserva ya fue cancelada o completada.')
    Schedule.objects.filter(pk=booking.schedule_id).update(available=F('available') + 1)
    User.objects.filter(pk=user.pk).update(credits=F('credits') + booking.sparks, points=F('points') - 50)
    Movement.objects.create(user=user, delta=booking.sparks, description='Devolución por cancelación', booking=booking)
    audit(user, 'cancel', booking)


@transaction.atomic
def complete(user, booking):
    if not Booking.objects.filter(pk=booking.pk, status='confirmed').update(status='completed'):
        raise ValidationError('Solo puedes completar reservas confirmadas.')
    Settlement.objects.create(booking=booking, organization=booking.schedule.activity.organization, amount=booking.amount)
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
