from django.urls import path
from django.contrib.auth import views as auth
from django.contrib.staticfiles.views import serve
from core import views as v
from core.admin import site

urlpatterns = [
    path('', v.home, name='home'),
    path('referencia/', v.reference, name='reference'),
    path('actividades/', v.explore, name='explore'),
    path('actividades/<int:pk>/', v.activity_detail, name='activity'),
    path('actividades/<int:pk>/favorito/', v.favorite, name='favorite'),
    path('registro/', v.register, name='register'),
    path('ingresar/', auth.LoginView.as_view(template_name='portal/form.html', extra_context={'title': 'Iniciar sesión'}), name='login'),
    path('salir/', auth.LogoutView.as_view(), name='logout'),
    path('cuenta/', v.profile, name='profile'),
    path('cuenta/clave/', auth.PasswordChangeView.as_view(template_name='portal/form.html', success_url='/panel/', extra_context={'title': 'Cambiar contraseña'}), name='password_change'),
    path('panel/', v.dashboard, name='dashboard'),
    path('planes/', v.plans, name='plans'),
    path('planes/<int:pk>/activar/', v.activate_plan, name='activate_plan'),
    path('mis-sparks/', v.wallet, name='wallet'),
    path('reservar/<int:pk>/', v.reserve, name='reserve'),
    path('reservas/', v.booking_list, name='bookings'),
    path('reservas/exportar/', v.export_bookings, name='export_bookings'),
    path('reservas/<int:pk>/<str:action>/', v.booking_action, name='booking_action'),
    path('opiniones/<int:pk>/crear/', v.review, name='review'),
    path('opiniones/<int:pk>/responder/', v.reply_review, name='reply_review'),
    path('reputacion/', v.reputation, name='reputation'),
    path('comprobantes/<int:pk>/', v.document, name='document'),
    path('organizaciones/', v.organizations_list, name='organizations'),
    path('organizaciones/registrar/', v.organization_register, name='organization_register'),
    path('solicitudes/', v.request_list, name='requests'),
    path('solicitudes/nueva/', v.request_create, name='request_create'),
    path('solicitudes/<int:pk>/', v.request_detail, name='request_detail'),
    path('gestion/<str:kind>/', v.management, name='management'),
    path('gestion/<str:kind>/crear/', v.edit_record, name='create_record'),
    path('gestion/<str:kind>/<int:pk>/editar/', v.edit_record, name='edit_record'),
    path('gestion/<str:kind>/<int:pk>/desactivar/', v.deactivate, name='deactivate'),
    path('aprobar-centro/<int:pk>/', v.approve_organization, name='approve_organization'),
    path('finanzas/', v.finance, name='finance'),
    path('finanzas/<int:pk>/retirar/', v.withdrawal, name='withdrawal'),
    path('finanzas/<int:pk>/cuenta/', v.bank, name='bank'),
    path('retiros/<int:pk>/<str:status>/', v.withdrawal_status, name='withdrawal_status'),
    path('superadmin/', site.urls),
    # Local demonstration only. Static files are served without exposing source/runtime files.
    path('static/<path:path>', serve, {'insecure': True}),
]
