import csv
from datetime import date
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.conf import settings
from . import models as m, forms as f, access, services


def public_activities():
    return m.Activity.objects.filter(active=True, organization__active=True, organization__approved=True).select_related('organization__city', 'category')


def home(request):
    return render(request, 'portal/home.html', {'activities': public_activities()[:6], 'activity_count': public_activities().count(), 'center_count': m.Organization.objects.filter(approved=True, active=True, kind='provider').count()})


def reference(request):
    html = (settings.BASE_DIR / 'Kiddo Spark B2B2C.html').read_text(encoding='utf-8')
    html = html.replace('href="assets/css/styles.css"', 'href="/static/css/styles.css"')
    html = html.replace('<body>', '<body><a href="/" style="position:fixed;bottom:12px;left:12px;z-index:99999;background:#0F2C59;color:white;padding:12px;border-radius:12px">Referencia original: datos simulados · Volver a plataforma</a>', 1)
    return HttpResponse(html)


def explore(request):
    qs = public_activities()
    for key, lookup in [('city', 'organization__city_id'), ('category', 'category_id')]:
        if request.GET.get(key, '').isdigit():
            qs = qs.filter(**{lookup: request.GET[key]})
    if request.GET.get('q'):
        qs = qs.filter(Q(name__icontains=request.GET['q']) | Q(organization__name__icontains=request.GET['q']) | Q(description__icontains=request.GET['q']))
    if request.GET.get('age', '').isdigit():
        qs = qs.filter(age_min__lte=int(request.GET['age']), age_max__gte=int(request.GET['age']))
    if request.GET.get('sparks', '').isdigit():
        qs = qs.filter(sparks__lte=int(request.GET['sparks']))
    if request.GET.get('favorites') and request.user.is_authenticated:
        qs = qs.filter(favorite__user=request.user)
    return render(request, 'portal/explore.html', {'page': Paginator(qs.order_by('name'), 12).get_page(request.GET.get('page')), 'categories': m.Category.objects.filter(active=True), 'cities': m.City.objects.filter(active=True)})


def activity_detail(request, pk):
    obj = get_object_or_404(public_activities(), pk=pk)
    return render(request, 'portal/activity.html', {'activity': obj, 'slots': obj.schedules.filter(active=True, starts_at__gt=timezone.now()).order_by('starts_at'), 'reviews': m.Review.objects.filter(booking__schedule__activity=obj).select_related('booking__user').order_by('-created_at'), 'favorite': request.user.is_authenticated and m.Favorite.objects.filter(user=request.user, activity=obj).exists()})


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = f.RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save()
            services.audit(user, 'register', user)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'portal/form.html', {'form': form, 'title': 'Crea tu cuenta', 'intro': 'Usa datos ficticios para esta demostración académica.'})


@login_required
def profile(request):
    form = f.ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado.')
        return redirect('dashboard')
    return render(request, 'portal/form.html', {'form': form, 'title': 'Mi perfil'})


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


@login_required
def dashboard(request):
    bookings = period_filter(request, access.bookings(request.user)).select_related('schedule__activity', 'user')
    requests = period_filter(request, access.requests(request.user))
    live = bookings.exclude(status='cancelled')
    totals = live.aggregate(sparks=Sum('sparks'), amount=Sum('amount'))
    series = list(live.annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).order_by('day'))
    max_count = max([x['count'] for x in series] or [1])
    for row in series:
        row['width'] = row['count'] * 100 // max_count
    return render(request, 'portal/dashboard.html', {'booking_count': bookings.count(), 'completed_count': bookings.filter(status='completed').count(), 'request_count': requests.count(), 'pending_count': requests.filter(status='pending').count(), 'totals': totals, 'recent_bookings': bookings.order_by('-created_at')[:5], 'series': series, 'popular': live.values('schedule__activity__name').annotate(count=Count('id')).order_by('-count')[:5], 'requests_by_status': requests.values('status').annotate(count=Count('id')), 'own_orgs': access.organizations(request.user), 'user_count': m.User.objects.count() if request.user.is_superuser else None})


def plans(request):
    return render(request, 'portal/plans.html', {'plans': m.Plan.objects.filter(active=True), 'calc_activities': public_activities()[:12]})


@login_required
@require_POST
def activate_plan(request, pk):
    services.activate_plan(request.user, get_object_or_404(m.Plan, pk=pk, active=True))
    messages.success(request, 'Plan activado en modo académico. Sparks añadidos; no se realizó ningún cobro.')
    return redirect('wallet')


@login_required
def wallet(request):
    return render(request, 'portal/wallet.html', {'movements': request.user.movements.select_related('booking', 'membership__plan').order_by('-created_at'), 'memberships': m.Membership.objects.filter(user=request.user).select_related('plan').order_by('-created_at')})


@login_required
@require_POST
def favorite(request, pk):
    obj = get_object_or_404(public_activities(), pk=pk)
    item, created = m.Favorite.objects.get_or_create(user=request.user, activity=obj)
    if not created:
        item.delete()
    return redirect('activity', pk=pk)


@login_required
@require_POST
def reserve(request, pk):
    slot = get_object_or_404(m.Schedule, pk=pk)
    try:
        services.reserve(request.user, slot.pk)
        messages.success(request, 'Reserva confirmada. Se descontaron los Sparks y se registraron 50 puntos.')
        return redirect('bookings')
    except (ValidationError, IntegrityError) as exc:
        messages.error(request, '; '.join(exc.messages) if isinstance(exc, ValidationError) else 'La reserva ya existe. Revisa tus reservas.')
    return redirect('activity', pk=slot.activity_id)


@login_required
def booking_list(request):
    qs = access.bookings(request.user).select_related('user', 'schedule__activity__organization')
    if request.GET.get('status') in dict(m.Booking.STATUS):
        qs = qs.filter(status=request.GET['status'])
    if request.GET.get('q'):
        qs = qs.filter(Q(schedule__activity__name__icontains=request.GET['q']) | Q(user__username__icontains=request.GET['q']))
    return render(request, 'portal/bookings.html', {'bookings': period_filter(request, qs).order_by('-created_at')})


@login_required
@require_POST
def booking_action(request, pk, action):
    obj = get_object_or_404(access.bookings(request.user).select_related('schedule__activity'), pk=pk)
    try:
        if action == 'cancel':
            services.cancel(request.user, obj)
        elif action == 'complete':
            access.require_manager(request.user, m.Booking)
            if not access.activities(request.user).filter(pk=obj.schedule.activity_id).exists():
                raise PermissionDenied
            services.complete(request.user, obj)
        else:
            raise Http404
        messages.success(request, 'Reserva actualizada.')
    except ValidationError as exc:
        messages.error(request, '; '.join(exc.messages))
    return redirect('bookings')


@login_required
def review(request, pk):
    booking = get_object_or_404(m.Booking, pk=pk, user=request.user, status='completed')
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
    access.require_manager(request.user, m.Review)
    obj = get_object_or_404(m.Review, pk=pk, booking__schedule__activity__in=access.activities(request.user))
    form = f.ResponseForm(request.POST or None, initial={'response': obj.response})
    if request.method == 'POST' and form.is_valid():
        obj.response = form.cleaned_data['response']
        obj.save(update_fields=['response'])
        return redirect('activity', pk=obj.booking.schedule.activity_id)
    return render(request, 'portal/form.html', {'form': form, 'title': 'Responder opinión'})


def organizations_list(request):
    kind = request.GET.get('kind', 'provider')
    qs = m.Organization.objects.filter(active=True, approved=True).select_related('city')
    if kind in dict(m.Organization.KINDS):
        qs = qs.filter(kind=kind)
    return render(request, 'portal/organizations.html', {'organizations': qs.order_by('name'), 'kind': kind})


@login_required
def organization_register(request):
    form = f.OrganizationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.save()
            services.audit(request.user, 'organization_request', obj)
        messages.success(request, 'Registro guardado. Un superadministrador debe aprobar el centro y asignar su administrador.')
        return redirect('requests')
    return render(request, 'portal/form.html', {'form': form, 'title': 'Registrar centro u organización', 'intro': 'El registro no concede permisos de administración automáticamente.'})


@login_required
def request_list(request):
    return render(request, 'portal/requests.html', {'requests': access.requests(request.user).select_related('organization').order_by('-created_at'), 'registrations': m.Organization.objects.filter(created_by=request.user)})


@login_required
def request_create(request):
    initial = {k: request.GET[k] for k in ['kind', 'organization'] if k in request.GET}
    form = f.ServiceRequestForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            m.RequestEvent.objects.create(request=obj, actor=request.user, status='pending', note='Solicitud recibida en la plataforma.')
            services.audit(request.user, 'request_create', obj)
        messages.success(request, 'Solicitud guardada. Puedes consultar su seguimiento.')
        return redirect('request_detail', pk=obj.pk)
    return render(request, 'portal/form.html', {'form': form, 'title': 'Nueva solicitud'})


@login_required
def request_detail(request, pk):
    obj = get_object_or_404(access.requests(request.user).select_related('user', 'organization'), pk=pk)
    form = f.TransitionForm(request.POST or None)
    may_manage = request.user.is_staff and request.user.has_perm('core.change_servicerequest') and (request.user.is_superuser or obj.organization_id in access.organizations(request.user).values_list('pk', flat=True))
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


CRUD = {'activities': (m.Activity, f.ActivityForm, 'Actividades'), 'schedules': (m.Schedule, f.ScheduleForm, 'Horarios y cupos'), 'organizations': (m.Organization, f.OrganizationForm, 'Organizaciones'), 'categories': (m.Category, f.CategoryForm, 'Categorías'), 'cities': (m.City, f.CityForm, 'Comunas'), 'plans': (m.Plan, f.PlanForm, 'Planes'), 'campaigns': (m.Campaign, f.CampaignForm, 'Campañas demo')}


def managed_queryset(user, kind):
    model = CRUD[kind][0]
    qs = model.objects.all()
    if user.is_superuser:
        return qs
    if kind in ['categories', 'cities', 'plans']:
        raise PermissionDenied('Este mantenedor es exclusivo del superadministrador.')
    if kind == 'organizations':
        return access.organizations(user)
    if kind == 'activities':
        return access.activities(user)
    return qs.filter(activity__in=access.activities(user))


@login_required
def management(request, kind='activities'):
    if kind not in CRUD:
        raise Http404
    model, _, title = CRUD[kind]
    access.require_manager(request.user, model, 'view')
    qs = managed_queryset(request.user, kind)
    return render(request, 'portal/management.html', {'items': qs.order_by('-pk'), 'kind': kind, 'title': title, 'crud': CRUD, 'can_add': request.user.has_perm(f'core.add_{model._meta.model_name}')})


@login_required
@transaction.atomic
def edit_record(request, kind, pk=None):
    if kind not in CRUD:
        raise Http404
    model, form_class, title = CRUD[kind]
    access.require_manager(request.user, model, 'change' if pk else 'add')
    if kind == 'organizations' and not pk and not request.user.is_superuser:
        raise PermissionDenied
    qs = managed_queryset(request.user, kind)
    if kind == 'schedules' and pk and request.method == 'POST':
        qs.filter(pk=pk).update(active=F('active'))
    obj = get_object_or_404(qs, pk=pk) if pk else None
    kwargs = {'user': request.user} if kind in ['activities', 'schedules', 'campaigns'] else {}
    form = form_class(request.POST or None, instance=obj, **kwargs)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            item = form.save(commit=False)
            if kind == 'organizations' and not pk:
                item.created_by = request.user
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
    model = CRUD[kind][0]
    access.require_manager(request.user, model, 'delete')
    obj = get_object_or_404(managed_queryset(request.user, kind), pk=pk)
    obj.active = False
    obj.save(update_fields=['active'])
    services.audit(request.user, 'deactivate', obj)
    messages.success(request, 'Registro desactivado. Se conserva el historial.')
    return redirect('management', kind=kind)


@login_required
@require_POST
def approve_organization(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied
    obj = get_object_or_404(m.Organization, pk=pk)
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


@login_required
def export_bookings(request):
    qs = period_filter(request, access.bookings(request.user)).select_related('user', 'schedule__activity')
    if request.GET.get('status') in dict(m.Booking.STATUS):
        qs = qs.filter(status=request.GET['status'])
    if request.GET.get('q'):
        qs = qs.filter(Q(schedule__activity__name__icontains=request.GET['q']) | Q(user__username__icontains=request.GET['q']))
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="KiddoSpark_reservas_DEMO.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Reserva', 'Usuario ficticio', 'Actividad', 'Fecha', 'Sparks', 'Monto referencial demo', 'Estado'])
    for obj in qs.order_by('-created_at'):
        writer.writerow([csv_safe(v) for v in [f'KS-{obj.pk}', obj.user.username, obj.schedule.activity.name, timezone.localtime(obj.schedule.starts_at).isoformat(), obj.sparks, obj.amount, obj.get_status_display()]])
    return response


@login_required
def reputation(request):
    access.require_manager(request.user, m.Review, 'view')
    qs = m.Review.objects.filter(booking__schedule__activity__in=access.activities(request.user)).select_related('booking__schedule__activity')
    return render(request, 'portal/reputation.html', {'reviews': qs.order_by('-created_at'), 'summary': qs.aggregate(average=Avg('rating'), count=Count('id')), 'distribution': qs.values('rating').annotate(count=Count('id')).order_by('-rating')})


@login_required
def document(request, pk):
    obj = get_object_or_404(access.bookings(request.user).select_related('schedule__activity'), pk=pk)
    body = f'KIDDO SPARK - COMPROBANTE DEMO\nReserva: KS-{obj.pk}\nActividad: {obj.schedule.activity.name}\nEstado: {obj.get_status_display()}\nSparks: {obj.sparks}\nMonto referencial: CLP {obj.amount}\n\nNo acredita pagos ni constituye documento tributario. Prototipo académico.'
    response = HttpResponse(body, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="KS-{obj.pk}_DEMO.txt"'
    return response
