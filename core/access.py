from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import Organization, Activity, Booking, ServiceRequest


def account_start(user):
    return {
        'superadmin': 'superadmin:index',
        'admin': 'platform_statistics',
        'provider': 'dashboard',
        'applicant': 'provider_submissions',
        'client': 'home',
    }[user.role]


def operates_platform(user):
    return user.is_superuser or (user.is_staff and user.has_perm('core.operate_platform'))


def require_manager(user, model, action='change'):
    model_name = model._meta.model_name
    if not user.is_staff or not user.has_perm(f'core.{action}_{model_name}'):
        raise PermissionDenied('No tienes permisos para esta operación.')
    if (model_name in {'settlement', 'withdrawal', 'bankaccount'}
            and not user.is_superuser and operates_platform(user)):
        raise PermissionDenied('La operación de plataforma no incluye finanzas de proveedores.')


def organizations(user):
    qs = Organization.objects.all()
    return qs if operates_platform(user) else qs.filter(administrators=user) if user.is_staff else qs.none()


def activities(user):
    return Activity.objects.filter(organization__in=organizations(user))


def bookings(user):
    qs = Booking.objects.all()
    if user.is_superuser:
        return qs
    if user.is_staff and user.has_perm('core.view_booking'):
        if operates_platform(user):
            return qs
        return qs.filter(Q(user=user) | Q(schedule__activity__organization__in=organizations(user))).distinct()
    return qs.filter(user=user)


def booking_approval_centers(user):
    if user.role == 'provider' and user.has_perm('core.change_booking'):
        return user.organizations.filter(kind='provider')
    return Organization.objects.none()


def requests(user):
    qs = ServiceRequest.objects.all()
    if user.is_superuser:
        return qs
    if user.is_staff and user.has_perm('core.view_servicerequest'):
        if operates_platform(user):
            return qs
        return qs.filter(Q(user=user) | Q(organization__in=organizations(user))).distinct()
    return qs.filter(user=user)
