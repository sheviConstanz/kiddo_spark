from datetime import timedelta
from io import StringIO
from runpy import run_module
from unittest.mock import patch
from django.contrib.auth.models import Permission
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse
from django.utils import timezone
from . import models as m, services, forms


class TunnelSettingsTests(SimpleTestCase):
    def test_exact_https_origin_and_separate_demo_data(self):
        origin = 'https://example-8001.usw2.devtunnels.ms'
        with patch.dict('os.environ', {'KIDDO_TUNNEL_ORIGIN': origin}):
            configuration = run_module('kiddo.tunnel_settings')
        self.assertEqual(configuration['CSRF_TRUSTED_ORIGINS'], [origin])
        self.assertEqual(configuration['ALLOWED_HOSTS'], ['example-8001.usw2.devtunnels.ms', '127.0.0.1'])
        self.assertEqual(configuration['DATABASES']['default']['NAME'].name, 'kiddo_tunnel.sqlite3')
        self.assertTrue(configuration['SESSION_COOKIE_SECURE'])

    def test_rejects_unrelated_or_malformed_origins(self):
        for origin in ('', 'http://example-8001.devtunnels.ms', 'https://example-8000.devtunnels.ms',
                       'https://example-8001.devtunnels.ms.example.invalid',
                       'https://example-8001.devtunnels.ms/'):
            with self.subTest(origin=origin), patch.dict('os.environ', {'KIDDO_TUNNEL_ORIGIN': origin}):
                with self.assertRaises(ImproperlyConfigured):
                    run_module('kiddo.tunnel_settings')


class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = m.User.objects.create_user('familia', email='familia@example.invalid', password='Family-Example!59', credits=26)
        cls.other = m.User.objects.create_user('otra', email='otra@example.invalid', password='Other-Example!59')
        cls.manager = m.User.objects.create_user('gestor', email='gestor@example.invalid', password='Manager-Example!59', is_staff=True)
        cls.manager.user_permissions.set(Permission.objects.filter(content_type__app_label='core').exclude(content_type__model='user'))
        cls.root = m.User.objects.create_superuser('super', 'super@example.invalid', 'Root-Example!59')
        cls.city = m.City.objects.create(name='Valparaíso')
        cls.cat = m.Category.objects.create(name='Deportes')
        cls.org = m.Organization.objects.create(name='Centro prueba', city=cls.city, created_by=cls.root, approved=True, email='centro@example.invalid')
        cls.org.administrators.add(cls.manager)
        cls.foreign_org = m.Organization.objects.create(name='Otro centro', city=cls.city, created_by=cls.root, approved=True, email='otro@example.invalid')
        cls.ally = m.Organization.objects.create(name='Aliado', kind='ally', city=cls.city, created_by=cls.root, approved=True, email='aliado@example.invalid')
        cls.ally.administrators.add(cls.manager)
        cls.activity = m.Activity.objects.create(name='Natación', organization=cls.org, category=cls.cat, description='Actividad de prueba', sparks=4, price=25000)
        cls.foreign_activity = m.Activity.objects.create(name='Actividad privada ajena', organization=cls.foreign_org, category=cls.cat, description='Otra', sparks=5)
        cls.slot = m.Schedule.objects.create(activity=cls.activity, starts_at=timezone.now() + timedelta(days=10), capacity=2, available=2)
        cls.plan = m.Plan.objects.create(name='Integral', sparks=26, price=34990)

    def auth(self, user=None):
        self.client.force_login(user or self.user)

    def test_public_pages_render_without_accounts(self):
        for url in ['/', '/actividades/', f'/actividades/{self.activity.pk}/', '/planes/', '/organizaciones/', '/organizaciones/?kind=ally', '/registro/', '/ingresar/', '/referencia/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_local_visual_resources_resolve(self):
        from django.contrib.staticfiles import finders
        for path in ['logo.png', 'css/styles.css', 'portal.css', 'portal-theme.css', 'portal-icons.svg', 'portal.js', 'admin/css/base.css']:
            with self.subTest(path=path):
                self.assertIsNotNone(finders.find(path))
                self.assertEqual(self.client.get('/static/' + path).status_code, 200)

    def test_home_presents_pilot_evidence_and_labels_convention_demo(self):
        response = self.client.get(reverse('home'))
        for phrase in ('58,72 %', '192 de 327', 'Meta operativa', 'Objetivo de experiencia',
                       'Panel de convenio', 'Ejemplo ilustrativo', 'Simulación'):
            self.assertContains(response, phrase)
        self.assertContains(response, f'href="{reverse("request_create")}?kind=agreement"')
        self.assertContains(response, f'href="{reverse("providers")}"')

    def test_dashboard_prioritizes_actions_for_each_role(self):
        dashboard = reverse('dashboard')
        offer = reverse('management', args=['activities'])
        capacity = reverse('management', args=['schedules'])
        review = reverse('provider_review_queue')
        self.auth()
        family = self.client.get(dashboard)
        self.assertContains(family, 'Mi cuenta familiar')
        self.assertContains(family, f'href="{reverse("bookings")}"')
        self.assertNotContains(family, f'href="{offer}"')
        self.assertNotContains(family, f'href="{review}"')
        self.auth(self.manager)
        provider = self.client.get(dashboard)
        self.assertContains(provider, 'Seller Center')
        self.assertContains(provider, f'href="{offer}"')
        self.assertContains(provider, f'href="{capacity}"')
        self.assertNotContains(provider, f'href="{review}"')
        self.auth(self.root)
        self.assertContains(self.client.get(dashboard), f'href="{review}"')

    def test_private_pages_require_login(self):
        for url in ['/panel/', '/reservas/', '/solicitudes/', '/mis-sparks/', '/cuenta/', '/gestion/activities/', '/finanzas/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_registration_ignores_privileged_fields(self):
        response = self.client.post('/registro/', {'username': 'nueva', 'email': 'NUEVA@example.invalid', 'password1': 'Safe-Demo-New!45', 'password2': 'Safe-Demo-New!45', 'is_staff': 'on', 'is_superuser': 'on', 'credits': 99999})
        self.assertEqual(response.status_code, 302)
        obj = m.User.objects.get(username='nueva')
        self.assertFalse(obj.is_staff)
        self.assertFalse(obj.is_superuser)
        self.assertEqual(obj.credits, 0)
        self.assertTrue(obj.check_password('Safe-Demo-New!45'))
        self.assertNotEqual(obj.password, 'Safe-Demo-New!45')
        self.assertEqual(obj.email, 'nueva@example.invalid')

    def test_duplicate_email_rejected_case_insensitively(self):
        form = forms.RegisterForm({'username': 'dup', 'email': 'FAMILIA@example.invalid', 'password1': 'Safe-Demo-New!45', 'password2': 'Safe-Demo-New!45'})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_login_logout_and_bad_password(self):
        self.assertFalse(self.client.login(username='familia', password='incorrect'))
        self.assertTrue(self.client.login(username='familia', password='Family-Example!59'))
        self.assertEqual(self.client.get('/panel/').status_code, 200)
        self.assertEqual(self.client.get('/salir/').status_code, 405)
        self.assertEqual(self.client.post('/salir/').status_code, 302)
        self.assertEqual(self.client.get('/panel/').status_code, 302)

    def test_all_user_and_admin_templates(self):
        self.auth()
        for url in ['/panel/', '/reservas/', '/solicitudes/', '/solicitudes/nueva/', '/organizaciones/registrar/', '/mis-sparks/', '/cuenta/', '/cuenta/clave/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.auth(self.manager)
        for url in ['/panel/', '/gestion/activities/', '/gestion/activities/crear/', '/gestion/schedules/crear/', '/gestion/organizations/', '/gestion/campaigns/crear/', '/finanzas/', f'/finanzas/{self.org.pk}/retirar/', f'/finanzas/{self.org.pk}/cuenta/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.auth(self.root)
        for url in ['/gestion/categories/', '/gestion/cities/crear/', '/gestion/plans/', '/superadmin/', '/superadmin/core/user/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_regular_user_cannot_access_management(self):
        self.auth()
        self.assertEqual(self.client.get('/gestion/activities/').status_code, 403)
        self.assertEqual(self.client.post(f'/aprobar-centro/{self.org.pk}/').status_code, 403)
        self.assertEqual(self.client.get('/finanzas/').status_code, 403)

    def test_staff_requires_model_permissions(self):
        self.manager.user_permissions.clear()
        self.auth(self.manager)
        self.assertEqual(self.client.get('/gestion/activities/').status_code, 403)
        booking = services.reserve(self.user, self.slot.pk)
        self.assertNotContains(self.client.get('/reservas/'), f'KS-{booking.pk}')

    def test_manager_scope_and_no_global_edit(self):
        self.auth(self.manager)
        self.assertNotContains(self.client.get('/gestion/activities/'), self.foreign_activity.name)
        self.assertEqual(self.client.get(f'/gestion/activities/{self.foreign_activity.pk}/editar/').status_code, 404)
        self.assertEqual(self.client.get('/gestion/plans/').status_code, 403)
        self.assertEqual(self.client.get('/superadmin/').status_code, 302)

    def test_plan_activation_persists_and_logs(self):
        services.activate_plan(self.user, self.plan)
        self.user.refresh_from_db()
        self.assertEqual(self.user.credits, 52)
        self.assertEqual(m.Membership.objects.get(user=self.user).sparks, 26)
        self.assertEqual(m.Movement.objects.get(user=self.user).delta, 26)

    def test_reserve_and_cancel_idempotence(self):
        booking = services.reserve(self.user, self.slot.pk)
        self.user.refresh_from_db(); self.slot.refresh_from_db()
        self.assertEqual((self.user.credits, self.user.points, self.slot.available), (22, 50, 1))
        services.cancel(self.user, booking)
        with self.assertRaises(ValidationError):
            services.cancel(self.user, booking)
        self.user.refresh_from_db(); self.slot.refresh_from_db()
        self.assertEqual((self.user.credits, self.user.points, self.slot.available), (26, 0, 2))
        self.assertEqual(m.Movement.objects.filter(booking=booking).count(), 2)

    def test_insufficient_balance_rolls_back_cupo(self):
        with self.assertRaises(ValidationError):
            services.reserve(self.other, self.slot.pk)
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.available, 2)
        self.assertEqual(m.Booking.objects.count(), 0)

    def test_full_schedule_does_not_debit(self):
        self.slot.available = 0; self.slot.save()
        with self.assertRaises(ValidationError):
            services.reserve(self.user, self.slot.pk)
        self.user.refresh_from_db()
        self.assertEqual(self.user.credits, 26)

    def test_duplicate_reservation_rolls_back(self):
        services.reserve(self.user, self.slot.pk)
        with self.assertRaises(ValidationError):
            services.reserve(self.user, self.slot.pk)
        self.slot.refresh_from_db(); self.user.refresh_from_db()
        self.assertEqual(self.slot.available, 1)
        self.assertEqual(self.user.credits, 22)

    def test_disabled_organization_blocks_new_reservations(self):
        self.org.approved = False; self.org.save()
        with self.assertRaises(ValidationError):
            services.reserve(self.user, self.slot.pk)
        self.assertEqual(self.client.get(f'/actividades/{self.activity.pk}/').status_code, 404)

    def test_expired_schedule_rejected(self):
        self.slot.starts_at = timezone.now() - timedelta(days=1); self.slot.save()
        with self.assertRaises(ValidationError):
            services.reserve(self.user, self.slot.pk)

    def test_other_user_cannot_cancel_or_download(self):
        b = services.reserve(self.user, self.slot.pk)
        self.auth(self.other)
        self.assertEqual(self.client.post(f'/reservas/{b.pk}/cancel/').status_code, 404)
        self.assertEqual(self.client.get(f'/comprobantes/{b.pk}/').status_code, 404)

    def test_complete_once_and_financial_balance(self):
        b = services.reserve(self.user, self.slot.pk)
        self.auth(self.manager)
        self.assertEqual(self.client.post(f'/reservas/{b.pk}/complete/').status_code, 302)
        with self.assertRaises(ValidationError): services.complete(self.manager, b)
        self.assertEqual(services.available_balance(self.org), 25000)
        self.assertEqual(m.Settlement.objects.count(), 1)

    def test_withdrawals_reserve_balance_and_reject_releases(self):
        b = services.reserve(self.user, self.slot.pk); services.complete(self.manager, b)
        w = services.withdraw(self.manager, self.org, 20000)
        self.assertEqual(services.available_balance(self.org), 5000)
        with self.assertRaises(ValidationError): services.withdraw(self.manager, self.org, 6000)
        self.auth(self.manager)
        self.assertEqual(self.client.post(f'/retiros/{w.pk}/paid/').status_code, 403)
        self.auth(self.root)
        self.client.post(f'/retiros/{w.pk}/rejected/')
        self.assertEqual(services.available_balance(self.org), 25000)

    def test_schedule_capacity_cannot_drop_below_occupied(self):
        services.reserve(self.user, self.slot.pk)
        data = {'activity': self.activity.pk, 'starts_at': self.slot.starts_at, 'capacity': 0, 'active': True}
        form = forms.ScheduleForm(data, instance=self.slot, user=self.manager)
        self.assertFalse(form.is_valid())
        self.assertIn('capacity', form.errors)

    def test_new_schedule_sets_available(self):
        form = forms.ScheduleForm({'activity': self.activity.pk, 'starts_at': timezone.now() + timedelta(days=20), 'capacity': 8, 'active': True}, user=self.manager)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().available, 8)

    def test_activity_form_rejects_other_organization(self):
        data = {'name': 'No permitido', 'organization': self.foreign_org.pk, 'category': self.cat.pk, 'description': 'Demo', 'age_min': 5, 'age_max': 10, 'sparks': 4, 'price': 0, 'icon': 'A', 'active': True}
        form = forms.ActivityForm(data, user=self.manager)
        self.assertFalse(form.is_valid())
        self.assertIn('organization', form.errors)

    def test_request_and_history_and_privacy(self):
        self.auth()
        response = self.client.post('/solicitudes/nueva/', {'kind': 'advice', 'organization': self.ally.pk, 'entity_name': 'Centro ficticio', 'subject': 'Contabilidad', 'message': 'Necesito orientación.'})
        self.assertEqual(response.status_code, 302)
        obj = m.ServiceRequest.objects.get()
        self.assertEqual(obj.events.count(), 1)
        self.assertContains(self.client.get(f'/solicitudes/{obj.pk}/'), 'Necesito orientación.')
        self.auth(self.other)
        self.assertEqual(self.client.get(f'/solicitudes/{obj.pk}/').status_code, 404)
        self.auth(self.manager)
        self.assertEqual(self.client.post(f'/solicitudes/{obj.pk}/', {'status': 'reviewing', 'note': 'Revisión iniciada'}).status_code, 302)
        obj.refresh_from_db()
        self.assertEqual(obj.status, 'reviewing')
        self.assertEqual(obj.events.count(), 2)
        with self.assertRaises(ValidationError): services.transition_request(self.manager, obj, 'completed', 'Saltar')

    def test_corporate_request_only_superadmin_manages(self):
        obj = m.ServiceRequest.objects.create(user=self.user, kind='agreement', entity_name='Colegio demo', subject='Convenio', message='Hola')
        self.auth(self.manager)
        self.assertEqual(self.client.get(f'/solicitudes/{obj.pk}/').status_code, 404)
        self.auth(self.root)
        self.assertEqual(self.client.get(f'/solicitudes/{obj.pk}/').status_code, 200)

    def test_review_requires_completion_and_is_unique(self):
        b = services.reserve(self.user, self.slot.pk)
        self.auth()
        self.assertEqual(self.client.get(f'/opiniones/{b.pk}/crear/').status_code, 404)
        services.complete(self.manager, b)
        self.client.post(f'/opiniones/{b.pk}/crear/', {'rating': 5, 'comment': '<script>alert(1)</script>'})
        self.client.post(f'/opiniones/{b.pk}/crear/', {'rating': 1, 'comment': 'Otro'})
        self.assertEqual(m.Review.objects.count(), 1)
        response = self.client.get(f'/actividades/{self.activity.pk}/')
        self.assertContains(response, '&lt;script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')

    def test_favorite_is_persistent_and_toggleable(self):
        self.auth()
        url = f'/actividades/{self.activity.pk}/favorito/'
        self.client.post(url)
        self.assertEqual(m.Favorite.objects.filter(user=self.user).count(), 1)
        self.assertContains(self.client.get('/actividades/?favorites=1'), 'Natación')
        self.client.post(url)
        self.assertEqual(m.Favorite.objects.count(), 0)

    def test_metrics_derive_from_actual_scoped_records(self):
        b = services.reserve(self.user, self.slot.pk)
        self.auth(self.manager)
        response = self.client.get('/panel/')
        self.assertEqual(response.context['booking_count'], 1)
        self.assertEqual(response.context['totals']['amount'], 25000)
        services.cancel(self.user, b)
        response = self.client.get('/panel/')
        self.assertEqual(response.context['totals']['amount'], None)
        self.assertEqual(response.context['booking_count'], 1)

    def test_csv_permissions_and_formula_injection(self):
        self.activity.name = '=HYPERLINK("evil")'; self.activity.save()
        services.reserve(self.user, self.slot.pk)
        self.auth()
        self.assertIn("'=HYPERLINK", self.client.get('/reservas/exportar/').content.decode('utf-8'))
        self.auth(self.other)
        self.assertNotContains(self.client.get('/reservas/exportar/'), 'HYPERLINK')

    def test_mutating_routes_require_post_and_csrf(self):
        self.auth()
        self.assertEqual(self.client.get(f'/reservar/{self.slot.pk}/').status_code, 405)
        secure_client = Client(enforce_csrf_checks=True)
        secure_client.force_login(self.user)
        self.assertEqual(secure_client.post(f'/planes/{self.plan.pk}/activar/').status_code, 403)

    def test_deactivation_preserves_history(self):
        b = services.reserve(self.user, self.slot.pk)
        self.auth(self.manager)
        self.assertEqual(self.client.post(f'/gestion/activities/{self.activity.pk}/desactivar/').status_code, 302)
        self.activity.refresh_from_db()
        self.assertFalse(self.activity.active)
        self.assertTrue(m.Booking.objects.filter(pk=b.pk).exists())

    def test_seed_is_repeatable_and_preserves_edits(self):
        output = StringIO()
        call_command('seed_demo', stdout=output)
        counts = (m.Activity.objects.count(), m.Organization.objects.count(), m.Schedule.objects.count())
        first = m.Activity.objects.get(origin_key='activity:1')
        first.description = 'Edición humana'; first.name = 'Nombre cambiado'; first.save()
        call_command('seed_demo', stdout=output)
        first.refresh_from_db()
        self.assertEqual(first.description, 'Edición humana')
        self.assertEqual(first.name, 'Nombre cambiado')
        self.assertEqual(counts, (m.Activity.objects.count(), m.Organization.objects.count(), m.Schedule.objects.count()))

    def test_invalid_bank_account_rejected(self):
        form = forms.BankForm({'bank': 'Demo', 'account_type': 'Ficticia', 'last_four': '123a'})
        self.assertFalse(form.is_valid())

    def test_invalid_request_target_rejected(self):
        form = forms.ServiceRequestForm({'kind': 'agreement', 'organization': self.ally.pk, 'entity_name': 'Demo', 'subject': 'Prueba', 'message': 'Demo'})
        self.assertFalse(form.is_valid())

    def test_dashboard_invalid_date_does_not_crash(self):
        self.auth()
        self.assertEqual(self.client.get('/panel/?from=wrong&to=2026-99-99').status_code, 200)

    def test_complete_user_journey_and_admin_workflow(self):
        self.auth(self.other)
        self.assertEqual(self.client.post(f'/planes/{self.plan.pk}/activar/').status_code, 302)
        self.assertEqual(self.client.post(f'/reservar/{self.slot.pk}/').status_code, 302)
        booking = m.Booking.objects.get(user=self.other)
        self.auth(self.manager)
        self.client.post(f'/reservas/{booking.pk}/complete/')
        self.auth(self.other)
        self.client.post(f'/opiniones/{booking.pk}/crear/', {'rating': 4, 'comment': 'Buena experiencia demo'})
        opinion = m.Review.objects.get(booking=booking)
        self.auth(self.manager)
        self.client.post(f'/opiniones/{opinion.pk}/responder/', {'response': 'Gracias por participar'})
        self.assertContains(self.client.get('/reputacion/'), 'Gracias por participar')
        self.assertEqual(self.client.post(f'/finanzas/{self.org.pk}/retirar/', {'amount': 10000}).status_code, 302)
        self.assertEqual(self.client.post(f'/finanzas/{self.org.pk}/cuenta/', {'bank': 'Banco Demo', 'account_type': 'Ficticia', 'last_four': '0000'}).status_code, 302)
        self.assertEqual(services.available_balance(self.org), 15000)
        self.assertContains(self.client.get('/finanzas/'), 'Banco Demo')

    def test_catalogue_crud_and_campaign(self):
        self.auth(self.manager)
        data = {'name': 'Actividad nueva', 'organization': self.org.pk, 'category': self.cat.pk, 'description': 'Desde el mantenedor', 'age_min': 6, 'age_max': 9, 'sparks': 5, 'price': 22000, 'icon': 'A', 'active': 'on'}
        self.assertEqual(self.client.post('/gestion/activities/crear/', data).status_code, 302)
        activity = m.Activity.objects.get(name='Actividad nueva')
        data['name'] = 'Actividad editada'
        self.assertEqual(self.client.post(f'/gestion/activities/{activity.pk}/editar/', data).status_code, 302)
        response = self.client.post('/gestion/campaigns/crear/', {'name': 'Campaña ficticia', 'activity': activity.pk, 'daily_budget': 5000, 'active': True})
        self.assertEqual(response.status_code, 302)
        campaign = m.Campaign.objects.get()
        self.client.post(f'/gestion/campaigns/{campaign.pk}/desactivar/')
        campaign.refresh_from_db(); self.assertFalse(campaign.active)

    def test_superadmin_create_user_has_required_email(self):
        self.auth(self.root)
        self.assertContains(self.client.get('/superadmin/core/user/add/'), 'name="email"')
        response = self.client.post('/superadmin/core/user/add/', {'username': 'nuevo_admin', 'email': 'nuevo_admin@example.invalid', 'password1': 'Another-Safe!98', 'password2': 'Another-Safe!98'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(m.User.objects.get(username='nuevo_admin').email, 'nuevo_admin@example.invalid')

    def test_organization_registration_no_automatic_privileges(self):
        self.auth()
        response = self.client.post(reverse('organization_register'), {
            'name': 'Academia nueva', 'kind': 'ally', 'city': self.city.pk, 'specialty': self.cat.pk,
            'email': 'academia@example.invalid', 'description': 'Demo', 'phone': '+56 000 000 000',
            'contact_first_name': 'Andrea', 'contact_last_name': 'Demo', 'demo_acknowledged': 'on',
            'approved': 'on', 'administrators': self.user.pk,
        })
        self.assertEqual(response.status_code, 302)
        org = m.Organization.objects.get(name='Academia nueva')
        self.assertEqual(org.kind, 'provider')
        self.assertFalse(org.approved)
        self.assertFalse(org.administrators.exists())
        self.user.refresh_from_db(); self.assertFalse(self.user.is_staff)

    def provider_payload(self, **overrides):
        return {
            'name': 'Taller ficticio', 'city': self.city.pk, 'specialty': self.cat.pk,
            'contact_first_name': 'Andrea', 'contact_last_name': 'Prueba',
            'email': 'taller@example.invalid', 'phone': '+56 000 000 000',
            'website': 'https://taller.example.invalid', 'demo_acknowledged': 'on',
            **overrides,
        }

    def submit_provider(self):
        self.auth()
        response = self.client.post(reverse('organization_register'), self.provider_payload())
        org = m.Organization.objects.get(name='Taller ficticio')
        self.assertRedirects(response, reverse('provider_submission', args=[org.pk]))
        return org

    def review_provider(self, org, status, note):
        self.auth(self.root)
        url = reverse('provider_review', args=[org.pk])
        response = self.client.post(url, {
            'revision': org.review_events.first().pk, 'status': status, 'note': note,
        })
        self.assertRedirects(response, url)

    def test_public_provider_entry_continues_account_creation_to_intake(self):
        entry = reverse('providers')
        registration = reverse('register')
        intake = reverse('organization_register')
        self.assertContains(self.client.get(entry), f'{registration}?next={intake}')
        self.assertRedirects(self.client.get(reverse('provider_submissions')), f"{reverse('login')}?next={reverse('provider_submissions')}")
        self.assertContains(self.client.get(registration, {'next': intake}), f'name="provider_next" value="{intake}"')
        response = self.client.post(registration, {
            'username': 'contacto-demo', 'email': 'contacto@example.invalid',
            'password1': 'Demo-Unique!9182', 'password2': 'Demo-Unique!9182',
            'provider_next': intake,
        })
        self.assertRedirects(response, intake)

    def test_provider_registration_requires_demo_acknowledgment_and_pilot_city(self):
        self.auth()
        outside = m.City.objects.create(name='Santiago')
        response = self.client.post(
            reverse('organization_register'), self.provider_payload(city=outside.pk, demo_acknowledged=''),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['form'].errors), {'city', 'demo_acknowledged'})
        self.assertFalse(m.Organization.objects.filter(created_by=self.user).exists())

    def test_pa01_pa02_provider_correction_then_approval_controls_catalog(self):
        org = self.submit_provider()
        status = m.ProviderReviewEvent.Status
        detail = reverse('provider_submission', args=[org.pk])
        queue = reverse('provider_review_queue')
        self.assertContains(self.client.get(reverse('provider_submissions')), status.PENDING.label)
        self.assertFalse(forms.ActivityForm(user=self.root).fields['organization'].queryset.filter(pk=org.pk).exists())
        activity = m.Activity.objects.create(
            organization=org, name='Básquet de demostración', category=self.cat, description='Demo',
        )
        slot = m.Schedule.objects.create(activity=activity, starts_at=self.slot.starts_at, capacity=2, available=2)
        public_detail = reverse('activity', args=[activity.pk])
        self.assertEqual(self.client.get(public_detail).status_code, 404)
        with self.assertRaises(ValidationError):
            services.reserve(self.user, slot.pk)

        self.auth(self.root)
        self.assertContains(self.client.get(queue), org.name)
        self.review_provider(org, status.REVIEWING, 'Revisión iniciada.')
        self.review_provider(org, status.OBSERVED, 'Aclara la disciplina ofrecida.')
        self.assertNotContains(self.client.get(queue), org.name)
        self.assertContains(self.client.get(queue, {'estado': status.OBSERVED}), org.name)

        self.auth()
        self.assertContains(self.client.get(detail), 'Aclara la disciplina ofrecida.')
        revision = org.review_events.first().pk
        response = self.client.post(detail, self.provider_payload(
            revision=revision, description='Básquet para principiantes.',
        ))
        self.assertRedirects(response, detail)
        org.refresh_from_db()
        self.assertFalse(org.approved)
        self.assertEqual(org.description, 'Básquet para principiantes.')
        self.assertEqual(org.review_events.first().actor, self.user)
        self.assertEqual(self.client.get(public_detail).status_code, 404)

        self.review_provider(org, status.REVIEWING, 'Revisión de la ficha corregida.')
        self.review_provider(org, status.APPROVED, 'Ficha de demostración validada.')
        org.refresh_from_db()
        self.assertTrue(org.approved)
        self.assertFalse(org.administrators.exists())
        decision = org.review_events.first()
        self.assertEqual(decision.actor, self.root)
        self.assertEqual(decision.note, 'Ficha de demostración validada.')
        self.assertIsNotNone(decision.created_at)
        self.assertContains(self.client.get(public_detail), activity.name)
        self.assertTrue(forms.ActivityForm(user=self.root).fields['organization'].queryset.filter(pk=org.pk).exists())

    def test_provider_review_rejects_skipped_states_stale_decision_and_missing_reason(self):
        org = self.submit_provider()
        self.auth(self.root)
        status = m.ProviderReviewEvent.Status
        url = reverse('provider_review', args=[org.pk])
        initial = org.review_events.first().pk
        response = self.client.post(url, {'status': status.APPROVED, 'revision': initial, 'note': 'Omitir revisión'})
        self.assertIn('status', response.context['form'].errors)
        self.assertRedirects(self.client.post(reverse('approve_organization', args=[org.pk])), url)
        self.review_provider(org, status.REVIEWING, 'En revisión.')
        response = self.client.post(url, {'status': status.APPROVED, 'revision': initial, 'note': 'Desde vista anterior'})
        self.assertIn('__all__', response.context['form'].errors)
        response = self.client.post(url, {'status': status.REJECTED, 'revision': org.review_events.first().pk, 'note': '  '})
        self.assertIn('note', response.context['form'].errors)
        self.review_provider(org, status.REJECTED, 'Fuera del alcance de la actividad piloto.')
        self.auth()
        detail = reverse('provider_submission', args=[org.pk])
        self.assertContains(self.client.get(detail), 'Fuera del alcance de la actividad piloto.')
        self.assertEqual(self.client.post(detail, self.provider_payload()).status_code, 403)
        org.refresh_from_db()
        self.assertFalse(org.approved)
        self.assertEqual(org.review_events.count(), 3)

    def test_provider_review_and_contact_are_private(self):
        org = self.submit_provider()
        owner_detail = reverse('provider_submission', args=[org.pk])
        review = reverse('provider_review', args=[org.pk])
        for user in (self.other, self.manager):
            self.auth(user)
            self.assertNotContains(self.client.get(reverse('provider_submissions')), org.name)
            self.assertEqual(self.client.get(owner_detail).status_code, 404)
            self.assertEqual(self.client.post(owner_detail, self.provider_payload()).status_code, 404)
            self.assertEqual(self.client.get(reverse('provider_review_queue')).status_code, 403)
            self.assertEqual(self.client.get(review).status_code, 403)
            self.assertEqual(self.client.post(review, {'status': 'approved'}).status_code, 403)
        self.assertEqual(org.review_events.count(), 1)

    def test_staff_cannot_complete_foreign_booking_even_as_owner(self):
        self.manager.credits = 20; self.manager.save()
        slot = m.Schedule.objects.create(activity=self.foreign_activity, starts_at=timezone.now() + timedelta(days=1), capacity=1, available=1)
        booking = services.reserve(self.manager, slot.pk)
        self.auth(self.manager)
        self.assertEqual(self.client.post(f'/reservas/{booking.pk}/complete/').status_code, 403)

    def test_database_enforces_email_case_insensitive_uniqueness(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            m.User.objects.create_user('dup_case', email='FAMILIA@example.invalid')

    def test_export_respects_status_filter(self):
        booking = services.reserve(self.user, self.slot.pk)
        self.auth()
        self.assertNotContains(self.client.get('/reservas/exportar/?status=completed'), f'KS-{booking.pk}')
