import csv
from datetime import date, timedelta
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import Case, Count, Exists, OuterRef, Subquery, Sum, Avg, Q, F, Value, When
from django.db.models.functions import Coalesce, TruncDate
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
from . import models as m, forms as f, access, metrics, relief, services


def public_activities():
    return m.Activity.objects.filter(active=True, organization__kind='provider', organization__active=True, organization__approved=True).select_related('organization__city', 'category')


def home(request):
    if not request.user.is_authenticated:
        return public_landing(request)
    if request.user.role != 'client':
        return redirect(access.account_start(request.user))
    upcoming = access.bookings(request.user).filter(
        status=m.Booking.Status.RESERVED, attendance_recorded=False, schedule__starts_at__gte=timezone.now(),
    ).select_related('schedule__activity__organization').order_by('schedule__starts_at', 'pk')
    return render(request, 'portal/client_home.html', {
        'upcoming': upcoming[:3],
        'activities': public_activities().order_by('name', 'pk')[:3],
    })


def public_landing(request):
    access.require_service_profile(request.user)
    if request.user.is_authenticated and request.user.role == 'client':
        return redirect('home')
    return render(request, 'portal/home.html', {'activities': public_activities()[:6], 'activity_count': public_activities().count(), 'center_count': m.Organization.objects.filter(approved=True, active=True, kind='provider').count()})


def reference(request):
    access.require_service_profile(request.user)
    html = (settings.BASE_DIR / 'Kiddo Spark B2B2C.html').read_text(encoding='utf-8')
    html = html.replace('href="assets/css/styles.css"', 'href="/static/css/styles.css"')
    html = html.replace('<body>', '<body><a href="/" style="position:fixed;bottom:12px;left:12px;z-index:99999;background:#0F2C59;color:white;padding:12px;border-radius:12px">Referencia original: datos simulados · Volver a plataforma</a>', 1)
    return HttpResponse(html)


def catalog_number(value):
    return int(value) if value.isascii() and value.isdecimal() and len(value) <= 18 else None


CATALOG_AGES = {'5-7': (5, 7), '8-10': (8, 10), '11-14': (11, 14)}
SCHOOL_DAYS = (2, 3, 4, 5, 6)  # Django week_day: Sunday=1.
CATALOG_PERIODS = {
    'morning': ('Mañana', Q(starts_at__week_day__in=SCHOOL_DAYS, starts_at__hour__lt=12)),
    'after-school': ('Después de clases',
                     Q(starts_at__week_day__in=SCHOOL_DAYS, starts_at__hour__gte=15, starts_at__hour__lt=20)),
    'weekend': ('Fin de semana', Q(starts_at__week_day__in=(7, 1))),
}
CATALOG_MAP_POSITIONS = {
    'Valparaíso': (18, 66), 'Viña del Mar': (36, 27),
    'Quilpué': (63, 49), 'Villa Alemana': (77, 76),
}


def explore(request):
    filters = request.GET
    favorite_access = request.user.is_authenticated and request.user.role != 'admin'
    qs = public_activities()
    for key, lookup in [('city', 'organization__city_id'), ('category', 'category_id')]:
        value = catalog_number(filters.get(key, ''))
        if value is not None:
            qs = qs.filter(**{lookup: value})
    search = filters.get('q', '').strip()
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(organization__name__icontains=search)
                       | Q(category__name__icontains=search) | Q(description__icontains=search))
    age = filters.get('age', '')
    age_range = CATALOG_AGES.get(age)
    exact_age = catalog_number(age)
    if age_range:
        qs = qs.filter(age_min__lte=age_range[1], age_max__gte=age_range[0])
    elif exact_age is not None:
        qs = qs.filter(age_min__lte=exact_age, age_max__gte=exact_age)
    if (sparks := catalog_number(filters.get('sparks', ''))) is not None:
        qs = qs.filter(sparks__lte=sparks)
    favorites_only = favorite_access and bool(filters.get('favorites'))
    if favorite_access:
        favorites = m.Favorite.objects.filter(activity=OuterRef('pk'), user=request.user)
        if favorites_only:
            qs = qs.filter(Exists(favorites))

    slots = m.Schedule.objects.filter(activity=OuterRef('pk'), active=True, starts_at__gt=timezone.now())
    if period := CATALOG_PERIODS.get(filters.get('period')):
        slots = slots.filter(period[1])
        qs = qs.filter(Exists(slots))
    if filters.get('available') == '1':
        qs = qs.filter(Exists(slots.filter(available__gt=0)))

    cities = list(m.City.objects.filter(active=True).order_by('name'))
    by_city = dict(qs.order_by().values('organization__city_id').annotate(total=Count('pk'))
                   .values_list('organization__city_id', 'total'))
    map_points = []
    for city in cities:
        if city.name in CATALOG_MAP_POSITIONS:
            x, y = CATALOG_MAP_POSITIONS[city.name]
            map_points.append({'city': city, 'x': x, 'y': y, 'count': by_city.get(city.pk, 0)})
    selected_city = next((city for city in cities if str(city.pk) == filters.get('city')), None)
    totals = slots.order_by().values('activity').annotate(total=Sum('available')).values('total')
    qs = qs.annotate(
        catalog_cupos=Coalesce(Subquery(totals), Value(0)),
        catalog_next=Subquery(slots.filter(available__gt=0).order_by('starts_at', 'pk').values('starts_at')[:1]),
    )
    if favorite_access:
        qs = qs.annotate(catalog_favorite=Exists(favorites))
    return render(request, 'portal/explore.html', {
        'page': Paginator(qs.order_by('name', 'pk'), 12).get_page(filters.get('page')),
        'categories': m.Category.objects.filter(active=True).order_by('name'),
        'cities': cities, 'map_points': map_points, 'selected_city': selected_city,
        'age_options': CATALOG_AGES, 'exact_age': exact_age,
        'period_options': [(key, period[0]) for key, period in CATALOG_PERIODS.items()],
        'favorites_only': favorites_only,
        'favorite_access': favorite_access,
    })


def activity_detail(request, pk):
    obj = get_object_or_404(public_activities(), pk=pk)
    slots = services.bookable_schedules().filter(activity=obj, available__gt=0).order_by('starts_at')
    favorite_access = request.user.is_authenticated and request.user.role != 'admin'
    return render(request, 'portal/activity.html', {
        'activity': obj, 'slots': slots,
        'reviews': m.Review.objects.filter(booking__schedule__activity=obj).select_related('booking__user').order_by('-created_at'),
        'favorite': favorite_access and m.Favorite.objects.filter(user=request.user, activity=obj).exists(),
        'favorite_access': favorite_access, 'may_reserve': access.may_reserve(request.user),
    })


class PortalLoginView(LoginView):
    template_name = 'portal/form.html'
    extra_context = {'title': 'Iniciar sesión'}

    def get_default_redirect_url(self):
        return reverse(access.account_start(self.request.user))


def register(request, for_provider=False):
    if request.user.is_authenticated:
        if for_provider:
            access.require_service_profile(request.user)
        if for_provider and request.user.role in {'provider', 'applicant'}:
            return redirect('organization_register')
        return redirect(access.account_start(request.user))
    next_url = (request.POST if request.method == 'POST' else request.GET).get('next')
    if not for_provider and request.method == 'GET' and next_url == reverse('organization_register'):
        return redirect('register_provider')
    return_to = next_url if not for_provider and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ) else None
    form = f.RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save(commit=False)
            user.provider_applicant = for_provider
            user.save()
            services.audit(user, 'register', user)
        login(request, user)
        return redirect('organization_register' if for_provider else return_to or 'home')
    return render(request, 'portal/form.html', {
        'form': form,
        'title': 'Crea tu cuenta de proveedor' if for_provider else 'Crea tu cuenta de cliente',
        'intro': 'Usa datos ficticios para esta demostración académica.',
        'next': return_to,
    })


@login_required
def profile(request):
    form = f.ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Guardamos los cambios de tu perfil.')
        return redirect('profile')
    return render(request, 'portal/profile_settings.html', {'form': form, 'title': 'Configuración de perfil'})


class PortalPasswordChangeView(PasswordChangeView):
    template_name = 'portal/password_change.html'
    success_url = reverse_lazy('profile')
    extra_context = {'title': 'Cambiar contraseña'}

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Tu contraseña se actualizó.')
        return response


def period_filter(request, qs):
    for key, lookup in [('from', 'created_at__date__gte'), ('to', 'created_at__date__lte')]:
        value = request.GET.get(key)
        if value:
            try:
                parsed = date.fromisoformat(value)
                qs = qs.filter(**{lookup: parsed})
            except ValueError:
                messages.error(request, 'Fecha inválida. Usa el formato año-mes-día.')
    return qs


def booking_trends(bookings):
    live = bookings.filter(status=m.Booking.Status.RESERVED)
    series = list(live.annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).order_by('day'))
    max_count = max([x['count'] for x in series] or [1])
    for row in series:
        row['width'] = row['count'] * 100 // max_count
    return {'series': series, 'popular': popular_activities(live)}


def popular_activities(bookings):
    return (
        bookings.values('schedule__activity_id', 'schedule__activity__name').annotate(count=Count('id'))
        .order_by('-count', 'schedule__activity__name', 'schedule__activity_id')[:5]
    )


@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return redirect('platform_operations')
    if request.user.role == 'applicant':
        return redirect('provider_submissions')
    own_orgs = access.organizations(request.user)
    bookings = access.bookings(request.user)
    if request.user.role == 'provider':
        return provider_statistics(request, own_orgs.filter(kind='provider'), bookings)
    bookings = period_filter(request, bookings)
    requests = period_filter(request, access.requests(request.user))
    return render(request, 'portal/dashboard.html', {
        'booking_count': bookings.count(),
        'completed_count': bookings.filter(attendance_recorded=True).count(),
        'request_count': requests.count(),
        'pending_count': requests.filter(status='pending').count(),
        'totals': bookings.filter(status=m.Booking.Status.RESERVED).aggregate(sparks=Sum('sparks'), amount=Sum('amount')),
        'own_orgs': own_orgs,
        'user_count': m.User.objects.count() if request.user.is_superuser else None,
        **booking_trends(bookings),
    })


def provider_statistics(request, centers, bookings, *, viewing_as_admin=False):
    centers = centers.select_related('city').order_by('name', 'pk')
    center_id = request.GET.get('center', '')
    selected_center = get_object_or_404(centers, pk=catalog_number(center_id)) if center_id else None
    scope = centers.filter(pk=selected_center.pk) if selected_center else centers
    activities = m.Activity.objects.filter(organization__in=scope).order_by('name', 'pk')
    activity_id = request.GET.get('activity', '')
    selected_activity = get_object_or_404(activities, pk=catalog_number(activity_id)) if activity_id else None
    measured = activities.filter(pk=selected_activity.pk) if selected_activity else activities
    bookings = bookings.filter(schedule__activity__in=measured)
    filtered = period_filter(request, bookings)
    if request.GET.get('export') == 'workshops':
        return export_workshop_metrics(filtered)
    return render(request, 'portal/provider_statistics.html', {
        'summary': metrics.center_metrics(
            filtered,
            services.bookable_schedules().filter(activity__in=measured),
            metrics.previous_period_count(bookings.filter(status=m.Booking.Status.RESERVED), request.GET),
        ),
        'centers': centers, 'selected_center': selected_center,
        'activities': activities, 'selected_activity': selected_activity,
        'metrics_url': reverse('platform_statistics' if viewing_as_admin else 'dashboard'),
        'viewing_as_admin': viewing_as_admin,
        **metrics.period_controls(),
    })


def export_workshop_metrics(bookings):
    response = HttpResponse('\ufeff', content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="KiddoSpark_rendimiento_talleres.csv"'
    writer = csv.writer(response)
    writer.writerow(['Taller', 'Reservas', 'Canceladas', 'Asistencias', 'Valor referencial demo CLP'])
    for row in metrics.workshop_rows(bookings):
        writer.writerow([csv_safe(row['schedule__activity__name']), row['reserved'], row['cancelled'],
                         row['attended'], row['demo_amount']])
    return response


@login_required
def platform_statistics(request):
    if not access.operates_platform(request.user):
        raise PermissionDenied
    providers = access.organizations(request.user).filter(kind='provider').select_related('city').order_by('name', 'pk')
    if request.GET.get('center'):
        return provider_statistics(request, providers, access.bookings(request.user), viewing_as_admin=True)
    bookings = period_filter(request, access.bookings(request.user))
    requests = period_filter(request, access.requests(request.user))
    booking_counts = dict(bookings.order_by().values('status').annotate(total=Count('pk')).values_list('status', 'total'))
    request_counts = dict(requests.order_by().values('status').annotate(total=Count('pk')).values_list('status', 'total'))
    booking_total = sum(booking_counts.values())
    published = public_activities()
    capacity = metrics.upcoming_capacity(services.bookable_schedules())
    live = bookings.filter(status=m.Booking.Status.RESERVED)
    city_name = 'schedule__activity__organization__city__name'
    cities = list(
        live.order_by().values_list(city_name)
        .annotate(total=Count('pk')).order_by('-total', city_name)[:5]
    )
    status = dict(
        provider_applications().order_by().values('review_stage').annotate(count=Count('pk'))
        .values_list('review_stage', 'count')
    )
    category_name = 'schedule__activity__category__name'
    categories = list(
        live.order_by().values_list(category_name)
        .annotate(total=Count('pk')).order_by('-total', category_name)[:6]
    )
    sparks = period_filter(request, m.Movement.objects.all()).aggregate(
        issued=Sum('delta', filter=Q(delta__gt=0, membership__isnull=False), default=0),
        applied=Sum('delta', filter=Q(delta__lt=0, booking__isnull=False), default=0),
        refunded=Sum('delta', filter=Q(delta__gt=0, booking__isnull=False), default=0),
    )
    sparks['applied'] = -sparks['applied']
    return render(request, 'portal/platform_statistics.html', {
        'booking_count': booking_total,
        'completed_count': bookings.filter(attendance_recorded=True).count(),
        'request_count': sum(request_counts.values()),
        'open_request_count': request_counts.get('pending', 0) + request_counts.get('reviewing', 0),
        'bookings_by_status': [(label, booking_counts.get(status, 0)) for status, label in m.Booking.STATUS],
        'requests_by_status': [(label, request_counts.get(status, 0)) for status, label in m.ServiceRequest.STATUS],
        'published_count': published.count(),
        'provider_count': providers.filter(approved=True, active=True).count(),
        'centers': providers,
        'onboarding': [(label, status.get(key, 0)) for key, label in m.ProviderReviewEvent.Status.choices],
        'onboarding_total': sum(status.values()),
        'categories': categories,
        'category_max': categories[0][1] if categories else 0,
        'sparks': sparks,
        'capacity': capacity,
        'timeline': metrics.booking_timeline(bookings),
        'providers_in_review': sum(status.get(stage, 0) for stage in (
            m.ProviderReviewEvent.Status.PENDING, m.ProviderReviewEvent.Status.REVIEWING,
        )),
        'popular': popular_activities(live),
        'cities': cities,
        'city_max': cities[0][1] if cities else 0,
        **metrics.period_controls(),
    })


REFERENCE_PLAN_BENEFITS = {
    'plan:Explorador': (
        'Reservas en todo el catálogo',
        '1 perfil familiar',
        'Compra de Sparks adicionales',
    ),
    'plan:Integral': (
        'Flexibilidad entre categorías',
        'Prioridad en alertas de cupo',
        '350 Spark Points iniciales demo',
    ),
    'plan:Full Spark': (
        'Mayor disponibilidad mensual',
        'Ideal para 2 o más actividades',
        'Compra preferente de packs demo',
    ),
}


def plans(request):
    access.require_service_profile(request.user)
    active_plans = m.Plan.objects.filter(active=True).order_by('price', 'sparks', 'pk')
    cards = [{
        'plan': plan,
        'name': plan.name if plan.name.casefold().startswith('plan ') else f'Plan {plan.name}',
        'price': f'{plan.price:,}'.replace(',', '.'),
        'benefits': REFERENCE_PLAN_BENEFITS.get(plan.origin_key, ()),
        'recommended': plan.origin_key == 'plan:Integral',
    } for plan in active_plans]
    return render(request, 'portal/plans.html', {
        'cards': cards,
        'show_reference_note': any(card['benefits'] for card in cards),
        'calc_activities': public_activities()[:12],
    })


@login_required
@require_POST
def activate_plan(request, pk):
    access.require_service_profile(request.user)
    services.activate_plan(request.user, get_object_or_404(m.Plan, pk=pk, active=True))
    messages.success(request, 'Plan activado en modo académico. Sparks añadidos; no se realizó ningún cobro.')
    return redirect('wallet')


@login_required
def wallet(request):
    access.require_service_profile(request.user)
    return render(request, 'portal/wallet.html', {'movements': request.user.movements.select_related('booking', 'membership__plan').order_by('-created_at'), 'memberships': m.Membership.objects.filter(user=request.user).select_related('plan').order_by('-created_at')})


@login_required
@require_POST
def favorite(request, pk):
    access.require_service_profile(request.user)
    obj = get_object_or_404(public_activities(), pk=pk)
    item, created = m.Favorite.objects.get_or_create(user=request.user, activity=obj)
    if not created:
        item.delete()
    if request.POST.get('from_catalog') == '1':
        return redirect(reverse('explore') + '?' + request.GET.urlencode())
    return redirect('activity', pk=pk)


@login_required
@require_POST
def reserve(request, pk):
    access.require_service_profile(request.user)
    slot = get_object_or_404(m.Schedule, pk=pk)
    try:
        services.reserve(request.user, slot.pk)
        messages.success(request, 'Reserva registrada. El cupo quedó confirmado y se descontaron tus Sparks.')
        return redirect('bookings')
    except (ValidationError, IntegrityError) as exc:
        messages.error(request, '; '.join(exc.messages) if isinstance(exc, ValidationError) else 'La reserva ya existe. Revisa tus reservas.')
    return redirect('activity', pk=slot.activity_id)


@login_required
def booking_list(request):
    bookings = filtered_bookings(request).select_related('schedule__activity__organization')
    return render(request, 'portal/bookings.html', {
        'bookings': bookings,
        'statuses': m.Booking.STATUS,
        'booking_centers': (
            access.organizations(request.user).filter(kind='provider').order_by('name', 'pk')
            if access.operates_platform(request.user) else []
        ),
        'managed_centers': (
            set(access.organizations(request.user).values_list('pk', flat=True))
            if request.user.role in {'provider', 'superadmin'} and request.user.has_perm('core.change_booking') else set()
        ),
    })


@login_required
@require_POST
def booking_action(request, pk, action):
    access.require_service_profile(request.user)
    obj = get_object_or_404(access.bookings(request.user).select_related('schedule__activity'), pk=pk)
    try:
        if action == 'cancel':
            services.cancel(request.user, obj)
            messages.success(request, 'Reserva cancelada. Se liberó el cupo y se devolvieron tus Sparks.')
        elif action == 'complete':
            access.require_manager(request.user, m.Booking)
            if not access.activities(request.user).filter(pk=obj.schedule.activity_id).exists():
                raise PermissionDenied
            services.complete(request.user, obj)
            messages.success(request, 'Asistencia registrada.')
        else:
            raise Http404
    except ValidationError as exc:
        messages.error(request, '; '.join(exc.messages))
    return redirect('bookings')


@login_required
def notifications(request):
    notices = Paginator(request.user.notifications.all(), 20).get_page(request.GET.get('page'))
    return render(request, 'portal/notifications.html', {'notices': notices})


@login_required
@require_POST
def read_notification(request, pk=None):
    notices = request.user.notifications.all()
    if pk is not None:
        notice = get_object_or_404(notices, pk=pk)
        notices = notices.filter(pk=notice.pk)
    notices.filter(read_at__isnull=True).update(read_at=timezone.now())
    return redirect('notifications')


@login_required
def review(request, pk):
    access.require_service_profile(request.user)
    booking = get_object_or_404(m.Booking, pk=pk, user=request.user, status=m.Booking.Status.RESERVED,
                                attendance_recorded=True)
    if m.Review.objects.filter(booking=booking).exists():
        messages.info(request, 'Ya has valorado esta reserva.')
        return redirect('bookings')
    form = f.ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.booking = booking
        obj.save()
        return redirect('activity', pk=booking.schedule.activity_id)
    return render(request, 'portal/form.html', {'form': form, 'title': 'Valorar experiencia'})


@login_required
def reply_review(request, pk):
    access.require_service_profile(request.user)
    access.require_manager(request.user, m.Review)
    obj = get_object_or_404(m.Review, pk=pk, booking__schedule__activity__in=access.activities(request.user))
    form = f.ResponseForm(request.POST or None, initial={'response': obj.response})
    if request.method == 'POST' and form.is_valid():
        obj.response = form.cleaned_data['response']
        obj.save(update_fields=['response'])
        return redirect('activity', pk=obj.booking.schedule.activity_id)
    return render(request, 'portal/form.html', {'form': form, 'title': 'Responder opinión'})


def organizations_list(request):
    access.require_service_profile(request.user)
    kind = request.GET.get('kind', 'provider')
    if kind == 'ally':
        return relief_home(request)
    if kind not in dict(m.Organization.KINDS):
        kind = 'provider'
    qs = m.Organization.objects.filter(kind=kind, active=True, approved=True).select_related('city')
    return render(request, 'portal/organizations.html', {'organizations': qs.order_by('name')})


def published_allies():
    return m.Organization.objects.filter(kind='ally', approved=True, active=True)


def relief_home(request):
    if request.user.is_authenticated and request.user.role == 'client':
        return redirect('home')
    can_request = not request.user.is_authenticated or request.user.role != 'admin'
    area = request.GET.get('area', '')
    selected_area = area if area in relief.AREA_CONTENT else ''
    qs = published_allies()
    if selected_area:
        qs = qs.filter(relief_area=selected_area)
    areas = [
        {'key': key, 'label': key.label, 'icon': icon, 'tone': tone, 'description': description}
        for key, (icon, tone, description, _) in relief.AREA_CONTENT.items()
    ]
    allies = []
    for organization in qs.order_by('name', 'pk'):
        icon, tone, *_ = relief.AREA_CONTENT.get(organization.relief_area, ('briefcase', 'ks-mint'))
        allies.append({'organization': organization, 'icon': icon, 'tone': tone})
    selected_needs = request.GET.getlist('need')
    suggestions = [area for area in areas if area['key'] in selected_needs and area['key'] in relief.DIAGNOSTIC_QUESTIONS]
    my_requests = None
    if can_request and request.user.is_authenticated:
        my_requests = request.user.service_requests.filter(kind__in=m.ServiceRequest.RELIEF_KINDS)
        my_requests = my_requests.select_related('organization').order_by('-created_at', '-pk')[:8]
    return render(request, 'portal/relief.html', {
        'allies': allies, 'areas': areas, 'selected_area': selected_area, 'my_relief_requests': my_requests,
        'can_request_relief': can_request,
        'diagnostic_questions': relief.DIAGNOSTIC_QUESTIONS, 'selected_needs': selected_needs,
        'diagnostic_submitted': request.GET.get('diagnostico') == '1', 'suggestions': suggestions,
    })


@login_required
def relief_request(request, request_kind, pk=None):
    access.require_service_profile(request.user)
    if request.user.role == 'client':
        raise PermissionDenied
    ally = get_object_or_404(published_allies(), pk=pk) if pk is not None else None
    area = relief.AREA_CONTENT.get(ally.relief_area) if ally else None
    default_topic = 'orientation' if ally is None else area[3] if area else 'other'
    form = f.ReliefRequestForm(request.POST if request.method == 'POST' else None, initial={
        'relief_topic': default_topic,
        'relief_channel': 'video',
    })
    titles = {'advice': 'Solicitar asesoría', 'quote': 'Pedir cotización', 'diagnosis': 'Solicitar orientación'}
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.kind = request_kind
        item.organization = ally
        item.subject = item.get_relief_topic_display()
        services.submit_request(request.user, item)
        messages.success(request, 'Solicitud guardada. Puedes seguir su estado desde Mis solicitudes.')
        return redirect('request_detail', pk=item.pk)
    return render(request, 'portal/relief_request.html', {'form': form, 'ally': ally, 'title': titles[request_kind]})


def providers(request):
    access.require_service_profile(request.user)
    if request.user.is_authenticated and request.user.role == 'client':
        return redirect('home')
    return render(request, 'portal/providers.html')


def provider_applications():
    event = m.ProviderReviewEvent.objects.filter(organization=OuterRef('pk')).values('status')[:1]
    return m.Organization.objects.filter(kind='provider').select_related('city', 'specialty').annotate(
        review_stage=Case(
            When(approved=True, then=Value(services.ProviderStatus.APPROVED)),
            default=Coalesce(Subquery(event), Value(services.ProviderStatus.PENDING)),
        ),
    ).order_by('-pk')


@login_required
def provider_submissions(request):
    access.require_service_profile(request.user)
    if request.user.role == 'client':
        raise PermissionDenied
    submissions = provider_applications().filter(created_by=request.user)
    return render(request, 'portal/provider_submissions.html', {'submissions': submissions})


@login_required
def organization_register(request):
    access.require_service_profile(request.user)
    if request.user.role == 'client':
        raise PermissionDenied
    form = f.ProviderForm(request.POST if request.method == 'POST' else None, initial={
        'contact_first_name': request.user.first_name, 'contact_last_name': request.user.last_name,
        'email': request.user.email,
    })
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            m.ProviderReviewEvent.objects.create(
                organization=obj, actor=request.user, status=services.ProviderStatus.PENDING,
                note='Ficha enviada para revisión en la demostración académica.',
            )
        messages.success(request, 'Solicitud recibida. Puedes seguir la revisión desde esta página.')
        return redirect('provider_submission', pk=obj.pk)
    return render(request, 'portal/provider_form.html', {'form': form, 'title': 'Registra tu centro'})


def provider_events(organization):
    return list(organization.review_events.select_related('actor'))


@login_required
def provider_submission(request, pk):
    access.require_service_profile(request.user)
    if request.user.role == 'client':
        raise Http404
    org = get_object_or_404(m.Organization.objects.select_related('city', 'specialty'), pk=pk, kind='provider', created_by=request.user)
    events = provider_events(org)
    status = services.provider_status(org, events[0] if events else None)
    correction = None
    if org.active and status == services.ProviderStatus.OBSERVED:
        correction = f.ProviderCorrectionForm(
            request.POST if request.method == 'POST' else None,
            instance=org, initial={'revision': events[0].pk},
        )
    if request.method == 'POST':
        if correction is None:
            raise PermissionDenied('Esta ficha no admite correcciones.')
        if correction.is_valid():
            updates = {field: correction.cleaned_data[field] for field in f.ProviderForm.Meta.fields}
            try:
                services.resubmit_provider(request.user, org, correction.cleaned_data['revision'], updates)
            except ValidationError as exc:
                correction.add_error(None, exc)
            else:
                messages.success(request, 'Ficha corregida y enviada nuevamente a revisión.')
                return redirect('provider_submission', pk=org.pk)
        org.refresh_from_db()
    return render(request, 'portal/provider_detail.html', {
        'organization': org, 'status': status, 'events': events, 'form': correction,
    })


@login_required
def provider_review_queue(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    statuses = services.ProviderStatus
    stage = request.GET.get('estado', statuses.PENDING)
    submissions = provider_applications()
    if stage in statuses.values:
        submissions = submissions.filter(review_stage=stage)
    return render(request, 'portal/provider_queue.html', {
        'page': Paginator(submissions, 20).get_page(request.GET.get('page')),
        'stage': stage, 'statuses': dict(statuses.choices),
    })


@login_required
def provider_review(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    org = get_object_or_404(m.Organization.objects.select_related('city', 'specialty'), pk=pk, kind='provider')
    events = provider_events(org)
    latest = events[0] if events else None
    status = services.provider_status(org, latest)
    next_states = services.PROVIDER_DECISIONS.get(status, ()) if org.active else ()
    form = None
    if request.method == 'POST' and not next_states:
        messages.error(request, 'La ficha ya no admite esta decisión.')
        return redirect('provider_review', pk=org.pk)
    if next_states:
        form = f.ProviderDecisionForm(
            request.POST if request.method == 'POST' else None, next_states=next_states,
            initial={'revision': latest.pk if latest else 0},
        )
        if request.method == 'POST' and form.is_valid():
            try:
                services.review_provider(request.user, org, **form.cleaned_data)
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, 'Decisión registrada en el historial de la ficha.')
                return redirect('provider_review', pk=org.pk)
    return render(request, 'portal/provider_detail.html', {
        'organization': org, 'status': status, 'events': events, 'form': form, 'admin_review': True,
    })


@login_required
def request_list(request):
    return render(request, 'portal/requests.html', {
        'requests': access.requests(request.user).select_related('organization').order_by('-created_at'),
        'registrations': m.Organization.objects.filter(created_by=request.user),
    })


@login_required
def request_create(request):
    initial = {k: request.GET[k] for k in ['kind', 'organization'] if k in request.GET}
    client_account = request.user.role == 'client'
    submitted_kind = (request.POST if request.method == 'POST' else request.GET).get('kind')
    if client_account and submitted_kind in {'demo', *m.ServiceRequest.RELIEF_KINDS}:
        raise PermissionDenied
    if client_account:
        initial['kind'] = 'agreement'
    form = f.ServiceRequestForm(request.POST or None, initial=initial, agreements_only=client_account)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        services.submit_request(request.user, obj)
        messages.success(request, 'Solicitud guardada. Puedes consultar su seguimiento.')
        return redirect('request_detail', pk=obj.pk)
    return render(request, 'portal/form.html', {
        'form': form, 'title': 'Solicitar un convenio' if client_account else 'Nueva solicitud',
    })


@login_required
def request_detail(request, pk):
    obj = get_object_or_404(access.requests(request.user).select_related('user', 'organization', 'preferred_city'), pk=pk)
    form = f.TransitionForm(request.POST or None)
    may_manage = (
        request.user.is_staff and request.user.has_perm('core.change_servicerequest')
        and (access.operates_platform(request.user)
             or access.organizations(request.user).filter(pk=obj.organization_id).exists())
    )
    if request.method == 'POST':
        if not may_manage:
            raise PermissionDenied
        if form.is_valid():
            try:
                services.transition_request(request.user, obj, form.cleaned_data['status'], form.cleaned_data['note'])
                return redirect('request_detail', pk=pk)
            except ValidationError as exc:
                form.add_error(None, exc)
    return render(request, 'portal/request_detail.html', {'item': obj, 'events': obj.events.select_related('actor').order_by('created_at'), 'form': form if may_manage else None})


CRUD = {
    'organizations': (m.Organization, f.OrganizationForm, 'Organizaciones'),
    'activities': (m.Activity, f.ActivityForm, 'Actividades'),
    'schedules': (m.Schedule, f.ScheduleForm, 'Horarios y cupos'),
    'categories': (m.Category, f.CategoryForm, 'Categorías'),
    'cities': (m.City, f.CityForm, 'Comunas'),
    'plans': (m.Plan, f.PlanForm, 'Planes'),
    'campaigns': (m.Campaign, f.CampaignForm, 'Campañas demo'),
}


def managed_queryset(user, kind):
    model = CRUD[kind][0]
    qs = model.objects.all()
    if kind == 'organizations' and user.role == 'admin':
        return qs.filter(kind='provider')
    if access.operates_platform(user):
        return qs
    if kind in ['categories', 'cities', 'plans']:
        raise PermissionDenied('Este mantenedor requiere acceso de administración de plataforma.')
    if kind == 'organizations':
        return access.organizations(user)
    if kind == 'activities':
        return access.activities(user)
    return qs.filter(activity__in=access.activities(user))


@login_required
def platform_operations(request):
    if not access.operates_platform(request.user):
        raise PermissionDenied
    for kind, (model, _, _) in CRUD.items():
        if request.user.has_perm(f'core.view_{model._meta.model_name}'):
            return redirect('management', kind=kind)
    raise PermissionDenied


@login_required
def management(request, kind='activities'):
    if kind not in CRUD:
        raise Http404
    model, _, title = CRUD[kind]
    access.require_manager(request.user, model, 'view')
    qs = managed_queryset(request.user, kind)
    provider_editor = kind == 'organizations' and access.may_edit_provider_records(request.user)
    if provider_editor:
        title = 'Proveedores'
    can_cancel_schedules = False
    if kind == 'schedules':
        centers = access.schedule_cancellation_centers(request.user)
        can_cancel_schedules = centers.exists()
        qs = qs.select_related('activity').annotate(can_cancel=Exists(centers.filter(pk=OuterRef('activity__organization_id'))))
    return render(request, 'portal/management.html', {
        'items': qs.order_by('-pk'), 'kind': kind, 'title': title,
        'can_add': (kind != 'organizations' or request.user.is_superuser)
                   and request.user.has_perm(f'core.add_{model._meta.model_name}'),
        'can_edit': provider_editor or request.user.has_perm(f'core.change_{model._meta.model_name}'),
        'can_deactivate': not provider_editor and request.user.has_perm(f'core.delete_{model._meta.model_name}'),
        'can_cancel_schedules': can_cancel_schedules,
        'cancellation_cutoff': services.schedule_cancellation_cutoff(timezone.now()),
    })


@login_required
@transaction.atomic
def edit_record(request, kind, pk=None):
    if kind not in CRUD:
        raise Http404
    model, form_class, title = CRUD[kind]
    provider_editor = bool(pk) and kind == 'organizations' and access.may_edit_provider_records(request.user)
    if not provider_editor:
        access.require_manager(request.user, model, 'change' if pk else 'add')
    else:
        title = 'Proveedores'
    if kind == 'organizations' and not pk and not request.user.is_superuser:
        raise PermissionDenied
    qs = managed_queryset(request.user, kind)
    if kind == 'schedules' and pk and request.method == 'POST':
        qs.filter(pk=pk).update(active=F('active'))
    obj = get_object_or_404(qs, pk=pk) if pk else None
    if kind == 'schedules' and obj and obj.cancelled_at:
        raise PermissionDenied('Un horario cancelado conserva su historial. Crea un horario nuevo.')
    kwargs = {'user': request.user} if kind in ['activities', 'schedules', 'campaigns'] else {}
    form = form_class(request.POST or None, instance=obj, **kwargs)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            item = form.save(commit=False)
            if kind == 'organizations' and not pk:
                item.created_by = request.user
            if kind == 'organizations' and pk:
                item.save(update_fields=[field for field in form.Meta.fields if field != 'kind'])
            else:
                item.save()
            services.audit(request.user, 'edit' if pk else 'create', item)
        messages.success(request, 'Cambios guardados.')
        return redirect('management', kind=kind)
    return render(request, 'portal/form.html', {'form': form, 'title': f'{"Editar" if pk else "Crear"} · {title}'})


@login_required
@require_POST
def deactivate(request, kind, pk):
    if kind not in CRUD:
        raise Http404
    if kind == 'schedules':
        raise PermissionDenied('Usa Cancelar horario para ingresar el motivo y avisar a los clientes.')
    if kind == 'organizations' and request.user.role == 'admin':
        raise PermissionDenied
    model = CRUD[kind][0]
    access.require_manager(request.user, model, 'delete')
    obj = get_object_or_404(managed_queryset(request.user, kind), pk=pk)
    obj.active = False
    obj.save(update_fields=['active'])
    services.audit(request.user, 'deactivate', obj)
    messages.success(request, 'Registro desactivado. Se conserva el historial.')
    return redirect('management', kind=kind)


@login_required
@require_http_methods(['GET', 'POST'])
def cancel_schedule(request, pk):
    centers = access.schedule_cancellation_centers(request.user)
    if not centers.exists():
        raise PermissionDenied
    schedule = get_object_or_404(
        m.Schedule.objects.filter(activity__organization__in=centers).select_related('activity'),
        pk=pk,
    )
    form = f.ScheduleCancellationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            services.cancel_schedule(request.user, schedule, form.cleaned_data['reason'])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, 'Horario cancelado. Se devolvieron los Sparks y se avisó a los clientes con reserva.')
            return redirect('management', kind='schedules')
    eligible = schedule.active and schedule.starts_at >= services.schedule_cancellation_cutoff(timezone.now())
    return render(request, 'portal/cancel_schedule.html', {'form': form, 'schedule': schedule, 'eligible': eligible})


@login_required
@require_POST
def approve_organization(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    obj = get_object_or_404(m.Organization, pk=pk)
    if obj.kind == 'provider':
        return redirect('provider_review', pk=obj.pk)
    obj.approved = True
    obj.save(update_fields=['approved'])
    services.audit(request.user, 'approve', obj)
    return redirect('management', kind='organizations')


@login_required
def finance(request):
    access.require_manager(request.user, m.Settlement, 'view')
    orgs = access.organizations(request.user).filter(kind='provider')
    balances = [{'organization': org, 'balance': services.available_balance(org)} for org in orgs]
    return render(request, 'portal/finance.html', {'balances': balances, 'settlements': m.Settlement.objects.filter(organization__in=orgs).select_related('booking', 'organization').order_by('-created_at'), 'withdrawals': m.Withdrawal.objects.filter(organization__in=orgs).select_related('organization').order_by('-created_at'), 'accounts': m.BankAccount.objects.filter(organization__in=orgs)})


@login_required
def withdrawal(request, pk):
    access.require_manager(request.user, m.Withdrawal, 'add')
    org = get_object_or_404(access.organizations(request.user), pk=pk, kind='provider')
    form = f.WithdrawalForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            services.withdraw(request.user, org, form.cleaned_data['amount'])
            messages.success(request, 'Solicitud de retiro demo registrada. No se transfirió dinero.')
            return redirect('finance')
        except ValidationError as exc:
            form.add_error(None, exc)
    return render(request, 'portal/form.html', {'form': form, 'title': f'Retiro demo · {org.name}', 'intro': f'Saldo ficticio disponible: ${services.available_balance(org):,}. No ingreses datos bancarios reales.'})


@login_required
@require_POST
def withdrawal_status(request, pk, status):
    if not request.user.is_superuser:
        raise PermissionDenied
    if status not in ['paid', 'rejected']:
        raise Http404
    if m.Withdrawal.objects.filter(pk=pk, status='pending').update(status=status):
        services.audit(request.user, 'withdrawal_' + status, m.Withdrawal.objects.get(pk=pk))
    return redirect('finance')


@login_required
def bank(request, pk):
    access.require_manager(request.user, m.BankAccount)
    org = get_object_or_404(access.organizations(request.user), pk=pk, kind='provider')
    form = f.BankForm(request.POST or None, instance=m.BankAccount.objects.filter(organization=org).first())
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.organization = org
        obj.save()
        return redirect('finance')
    return render(request, 'portal/form.html', {'form': form, 'title': 'Cuenta ficticia de liquidación', 'intro': 'Usa únicamente nombres y cuatro dígitos ficticios. No se conectará a un banco.'})


def csv_safe(value):
    text = str(value)
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else text


def filtered_bookings(request):
    qs = period_filter(request, access.bookings(request.user)).select_related('user', 'schedule__activity')
    if request.GET.get('status') in dict(m.Booking.STATUS):
        qs = qs.filter(status=request.GET['status'])
    if request.GET.get('q'):
        qs = qs.filter(Q(schedule__activity__name__icontains=request.GET['q']) | Q(user__username__icontains=request.GET['q']))
    if access.operates_platform(request.user) and request.GET.get('center'):
        qs = qs.filter(schedule__activity__organization_id=catalog_number(request.GET['center']))
    return qs.order_by('-created_at', '-pk')


@login_required
def export_bookings(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="KiddoSpark_reservas_DEMO.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Reserva', 'Usuario ficticio', 'Actividad', 'Fecha', 'Sparks', 'Monto referencial demo', 'Estado'])
    for obj in filtered_bookings(request):
        writer.writerow([csv_safe(v) for v in [f'KS-{obj.pk}', obj.user.username, obj.schedule.activity.name, timezone.localtime(obj.schedule.starts_at).isoformat(), obj.sparks, obj.amount, obj.get_status_display()]])
    return response


@login_required
def reputation(request):
    access.require_service_profile(request.user)
    access.require_manager(request.user, m.Review, 'view')
    qs = m.Review.objects.filter(booking__schedule__activity__in=access.activities(request.user)).select_related('booking__schedule__activity')
    return render(request, 'portal/reputation.html', {'reviews': qs.order_by('-created_at'), 'summary': qs.aggregate(average=Avg('rating'), count=Count('id')), 'distribution': qs.values('rating').annotate(count=Count('id')).order_by('-rating')})


@login_required
def document(request, pk):
    bookings = access.bookings(request.user).select_related('schedule__activity')
    obj = get_object_or_404(bookings, pk=pk)
    body = f'KIDDO SPARK - COMPROBANTE DEMO\nReserva: KS-{obj.pk}\nActividad: {obj.schedule.activity.name}\nEstado: {obj.get_status_display()}\nSparks: {obj.sparks}\nMonto referencial: CLP {obj.amount}\n\nNo acredita pagos ni constituye documento tributario. Prototipo académico.'
    response = HttpResponse(body, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="KS-{obj.pk}_DEMO.txt"'
    return response
