from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Organization, Activity, Booking, ServiceRequest


def require_manager(user, model, action='change'):
    if not user.is_staff or not user.has_perm(f'core.{action}_{model._meta.model_name}'):
        raise PermissionDenied('No tienes permisos para esta operación.')


def organizations(user):
    qs = Organization.objects.all()
    return qs if user.is_superuser else qs.filter(administrators=user) if user.is_staff else qs.none()


def activities(user):
    return Activity.objects.filter(organization__in=organizations(user))


def bookings(user):
    qs = Booking.objects.all()
    if user.is_superuser:
        return qs
    if user.is_staff and user.has_perm('core.view_booking'):
        return qs.filter(Q(user=user) | Q(schedule__activity__organization__in=organizations(user))).distinct()
    return qs.filter(user=user)


def requests(user):
    qs = ServiceRequest.objects.all()
    if user.is_superuser:
        return qs
    if user.is_staff and user.has_perm('core.view_servicerequest'):
        return qs.filter(Q(user=user) | Q(organization__in=organizations(user))).distinct()
    return qs.filter(user=user)
