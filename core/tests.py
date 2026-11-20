from datetime import datetime, timedelta
from importlib import import_module
from io import StringIO
from runpy import run_module
from types import SimpleNamespace
from unittest.mock import patch
from django.apps import apps
from django.contrib.auth.models import Permission
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
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
        self.assertFalse(configuration['KIDDO_SEED_DEMO_ACCOUNTS'])

    def test_rejects_unrelated_or_malformed_origins(self):
        for origin in ('', 'http://example-8001.devtunnels.ms', 'https://example-8000.devtunnels.ms',
                       'https://example-8001.devtunnels.ms.example.invalid',
                       'https://example-8001.devtunnels.ms/'):
            with self.subTest(origin=origin), patch.dict('os.environ', {'KIDDO_TUNNEL_ORIGIN': origin}):
                with self.assertRaises(ImproperlyConfigured):
                    run_module('kiddo.tunnel_settings')


class DemoAccountTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.activity = m.Activity.objects.get(origin_key='demo:operator-activity')
        cls.center = cls.activity.organization
        cls.family = m.User.objects.get(username='usuario')
        cls.other_center = m.Organization.objects.create(
            name='Centro ajeno a proveedor demo', city=cls.center.city, email='otro@example.invalid',
            created_by=cls.family, approved=True,
        )
        cls.other_activity = m.Activity.objects.create(
            organization=cls.other_center, name='Actividad de otro centro',
            category=cls.activity.category, description='Otro centro ficticio',
        )

    def login_profile(self, username):
        response = self.client.post(reverse('login'), {'username': username, 'password': username})
        target = {'superadmin': 'superadmin:index', 'admin': 'platform_statistics',
                  'usuario': 'home', 'proveedor': 'dashboard'}[username]
        self.assertRedirects(response, reverse(target))

    def test_data_migration_creates_four_login_profiles(self):
        expected = {
            'superadmin': ('correo@superadmin.cl', True, True),
            'admin': ('admin@demo.example.invalid', True, False),
            'usuario': ('usuario@demo.example.invalid', False, False),
            'proveedor': ('proveedor@demo.example.invalid', True, False),
        }
        for username, (email, staff, root) in expected.items():
            with self.subTest(username=username):
                self.client.logout()
                self.login_profile(username)
                user = m.User.objects.get(username=username)
                self.assertEqual((user.email, user.is_staff, user.is_superuser), (email, staff, root))
                self.assertNotEqual(user.password, username)
        self.assertTrue(self.center.approved)
        self.assertTrue(self.activity.schedules.filter(starts_at__gt=timezone.now(), available__gt=0).exists())

    def test_admin_edits_platform_catalogue_and_requests_but_cannot_use_sensitive_routes(self):
        self.login_profile('admin')
        categories = reverse('management', args=['categories'])
        edit = reverse('edit_record', args=['categories', self.activity.category_id])
        response = self.client.get(categories)
        self.assertContains(response, edit)
        self.assertNotContains(response, reverse('superadmin:core_user_changelist'))
        self.assertRedirects(self.client.post(edit, {'name': 'Categoría actualizada', 'active': 'on'}), categories)
        self.assertEqual(m.Category.objects.get(pk=self.activity.category_id).name, 'Categoría actualizada')
        foreign_activity_edit = reverse('edit_record', args=['activities', self.other_activity.pk])
        self.assertEqual(self.client.get(foreign_activity_edit).status_code, 200)
        request_record = m.ServiceRequest.objects.create(
            user=self.family, kind='agreement', entity_name='Colegio ficticio',
            subject='Convenio', message='Prueba con otro usuario',
        )
        request_url = reverse('request_detail', args=[request_record.pk])
        self.assertRedirects(self.client.post(request_url, {'status': 'reviewing', 'note': 'Revisión demo'}), request_url)

        for url in (reverse('superadmin:core_user_changelist'), reverse('superadmin:auth_group_changelist')):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/superadmin/login/', response.url)
            denied = self.client.post(url, {'action': 'delete_selected'})
            self.assertEqual(denied.status_code, 302)
            self.assertIn('/superadmin/login/', denied.url)
        # An extra grant from an operator group must not extend a global role to finance.
        admin = m.User.objects.get(username='admin')
        finance_permissions = Permission.objects.filter(
            content_type__app_label='core',
            codename__in=('view_settlement', 'change_bankaccount', 'add_withdrawal'),
        )
        admin.user_permissions.add(*finance_permissions)
        for url in (reverse('finance'), reverse('bank', args=[self.center.pk]),
                    reverse('withdrawal', args=[self.center.pk]), reverse('provider_review_queue')):
            self.assertEqual(self.client.get(url).status_code, 403)
        bank = reverse('bank', args=[self.center.pk])
        self.assertEqual(self.client.post(bank, {'bank': 'Prueba', 'account_type': 'Demo', 'last_four': '1234'}).status_code, 403)
        self.assertFalse(m.BankAccount.objects.filter(organization=self.center).exists())

    def test_provider_operates_only_the_assigned_center_and_family_reservation(self):
        self.login_profile('usuario')
        self.assertEqual(self.client.get(reverse('management', args=['activities'])).status_code, 403)
        plan = m.Plan.objects.create(name='Plan para el recorrido demo', sparks=10)
        self.client.post(reverse('activate_plan', args=[plan.pk]))
        slot = self.activity.schedules.get()
        self.assertRedirects(self.client.post(reverse('reserve', args=[slot.pk])), reverse('bookings'))
        booking = self.family.bookings.get(schedule=slot)
        self.assertEqual(booking.status, m.Booking.Status.RESERVED)
        self.assertContains(self.client.get(reverse('bookings')), 'Reservado')
        self.assertContains(self.client.get(reverse('document', args=[booking.pk])), 'Reservado')
        self.assertContains(self.client.get(reverse('notifications')), 'Reserva registrada')

        self.client.logout()
        self.login_profile('admin')
        stats = self.client.get(reverse('platform_statistics')).context
        self.assertEqual(dict(stats['bookings_by_status'])['Reservado'], 1)
        self.assertTrue(stats['timeline']['days'])

        self.client.logout()
        self.login_profile('proveedor')
        activities = self.client.get(reverse('management', args=['activities']))
        self.assertContains(activities, self.activity.name)
        self.assertNotContains(activities, self.other_activity.name)
        foreign_edit = reverse('edit_record', args=['activities', self.other_activity.pk])
        self.assertEqual(self.client.post(foreign_edit, {'name': 'Cambio indebido'}).status_code, 404)
        self.assertEqual(self.client.get(reverse('management', args=['categories'])).status_code, 403)
        self.assertContains(self.client.get(reverse('bookings')), f'KS-{booking.pk}')
        complete = reverse('booking_action', args=[booking.pk, 'complete'])
        self.assertEqual(m.Movement.objects.filter(booking=booking).count(), 1)
        self.assertRedirects(self.client.post(complete), reverse('bookings'))
        booking.refresh_from_db()
        self.assertEqual(booking.status, m.Booking.Status.RESERVED)
        self.assertTrue(booking.attendance_recorded)

        self.client.logout()
        self.login_profile('superadmin')
        self.assertEqual(self.client.get(reverse('superadmin:core_user_changelist')).status_code, 200)
        self.assertEqual(self.client.get(reverse('bank', args=[self.center.pk])).status_code, 200)

    def test_admin_uses_operations_and_cannot_take_part_in_service_flows(self):
        self.login_profile('admin')
        operations = reverse('platform_operations')
        providers = reverse('management', args=['organizations'])
        self.assertRedirects(self.client.get(reverse('dashboard')), operations, fetch_redirect_response=False)
        self.assertRedirects(self.client.get(operations), providers)
        response = self.client.get(providers)
        self.assertContains(response, '<h1>Proveedores</h1>', html=True)
        self.assertContains(response, '<table>')
        self.assertNotContains(response, 'class="module-nav"')
        self.assertContains(response, 'id="workspace-links"')
        self.assertNotContains(response, 'Actividad de la cuenta')
        for module in ('organizations', 'activities', 'schedules'):
            self.assertContains(response, reverse('management', args=[module]))
        slot = self.activity.schedules.get()
        for route, args in (('providers', []), ('register_provider', []),
                            ('organization_register', []), ('plans', []), ('reputation', [])):
            self.assertEqual(self.client.get(reverse(route, args=args)).status_code, 403)
        self.assertContains(self.client.get(reverse('explore')), self.activity.name)
        detail = self.client.get(reverse('activity', args=[self.activity.pk]))
        self.assertContains(detail, self.activity.name)
        self.assertNotContains(detail, f'action="{reverse("reserve", args=[slot.pk])}"')
        self.assertNotContains(detail, 'Guardar en favoritos')
        self.assertEqual(self.client.post(reverse('organization_register'), {'name': 'Alta indebida'}).status_code, 403)
        self.assertEqual(self.client.post(reverse('reserve', args=[slot.pk])).status_code, 403)
        self.assertFalse(m.Booking.objects.exists())

        other = m.Organization.objects.create(
            name='Organización fuera de alcance', kind='ally', city=self.center.city, created_by=self.family,
        )
        listing = self.client.get(reverse('management', args=['organizations']))
        self.assertContains(listing, self.center.name)
        self.assertNotContains(listing, other.name)
        self.assertEqual(self.client.get(reverse('edit_record', args=['organizations', other.pk])).status_code, 404)
        edit = reverse('edit_record', args=['organizations', self.center.pk])
        self.assertRedirects(self.client.post(edit, {
            'name': 'Centro actualizado por administración', 'city': self.center.city_id,
            'email': self.center.email, 'kind': 'ally', 'approved': 'false', 'active': '',
        }), reverse('management', args=['organizations']))
        self.center.refresh_from_db()
        self.assertEqual(self.center.name, 'Centro actualizado por administración')
        self.assertEqual((self.center.kind, self.center.active, self.center.approved), ('provider', True, True))

    def test_admin_lists_filters_and_exports_all_platform_bookings(self):
        mine = self.activity.schedules.get()
        foreign = m.Schedule.objects.create(activity=self.other_activity, starts_at=mine.starts_at, capacity=1, available=1)
        booking = m.Booking.objects.create(user=self.family, schedule=mine, sparks=1, amount=0)
        another = m.Booking.objects.create(user=self.family, schedule=foreign, sparks=1, amount=0)
        self.login_profile('admin')
        path = reverse('bookings')
        response = self.client.get(path)
        for item in (booking, another):
            self.assertContains(response, f'id="reserva-{item.pk}"')
        filters = {'center': self.other_center.pk, 'status': 'reserved', 'q': self.family.username,
                   'from': timezone.localdate().isoformat(), 'to': timezone.localdate().isoformat()}
        filtered = self.client.get(path, filters)
        self.assertContains(filtered, f'id="reserva-{another.pk}"')
        self.assertNotContains(filtered, f'id="reserva-{booking.pk}"')
        self.assertNotContains(filtered, 'Validar asistencia')
        csv = self.client.get(reverse('export_bookings'), filters)
        self.assertContains(csv, f'KS-{another.pk},')
        self.assertNotContains(csv, f'KS-{booking.pk},')
        self.assertEqual(self.client.post(reverse('booking_action', args=[another.pk, 'complete'])).status_code, 403)

    def test_data_migration_leaves_existing_accounts_and_conflicting_emails_intact(self):
        admin = m.User.objects.get(username='admin')
        old_permissions = set(admin.user_permissions.values_list('pk', flat=True))
        admin.email = 'cuenta-existente@example.invalid'
        admin.set_password('Existing-Test-Password-482!')
        admin.save()
        self.family.username = 'familia_existente'
        self.family.save(update_fields=['username'])

        migration = import_module('core.migrations.0006_local_demo_accounts')
        migration.create_local_accounts(apps, SimpleNamespace(connection=connection))
        admin.refresh_from_db()
        self.assertEqual(admin.email, 'cuenta-existente@example.invalid')
        self.assertTrue(admin.check_password('Existing-Test-Password-482!'))
        self.assertEqual(set(admin.user_permissions.values_list('pk', flat=True)), old_permissions)
        self.assertFalse(m.User.objects.filter(username='usuario').exists())
        self.assertTrue(m.User.objects.filter(username='familia_existente', pk=self.family.pk).exists())

    def test_provider_cannot_reserve_and_only_assigned_operators_get_new_booking_notice(self):
        operator = m.User.objects.get(username='proveedor')
        m.User.objects.filter(pk__in=(operator.pk, self.family.pk)).update(credits=25)
        outside = m.User.objects.create_user('operador_ajeno', email='operador-ajeno@example.invalid', is_staff=True)
        outside.user_permissions.add(Permission.objects.get(content_type__app_label='core', codename='view_booking'))
        self.other_center.administrators.add(outside)
        no_booking_permission = m.User.objects.create_user('contacto_centro', email='contacto-centro@example.invalid', is_staff=True)
        self.center.administrators.add(no_booking_permission)
        slot = self.activity.schedules.get()
        reserve = reverse('reserve', args=[slot.pk])
        detail = reverse('activity', args=[self.activity.pk])

        self.client.force_login(operator)
        self.assertNotContains(self.client.get(detail), f'action="{reserve}"')
        self.assertEqual(self.client.post(reserve).status_code, 403)
        slot.refresh_from_db()
        operator.refresh_from_db()
        self.assertEqual((slot.available, operator.credits), (8, 25))
        self.assertFalse(m.Booking.objects.exists())

        self.client.force_login(self.family)
        self.assertRedirects(self.client.post(reserve), reverse('bookings'))
        notice = operator.notifications.get()
        self.assertEqual(notice.kind, m.Notification.Kind.BOOKING_RECEIVED)
        self.assertEqual(notice.booking.user_id, self.family.pk)
        self.assertFalse(outside.notifications.exists())
        self.assertFalse(no_booking_permission.notifications.exists())
        self.client.force_login(operator)
        self.assertContains(self.client.get(reverse('notifications')), 'Nueva reserva en tu centro')
        self.assertContains(self.client.get(reverse('bookings')), f'id="reserva-{notice.booking_id}"')


    def test_main_navigation_stays_visible_and_account_links_use_header_dropdown(self):
        public_routes = ('home', 'explore', 'providers', 'plans', 'relief_home')
        main_links = (*map(reverse, public_routes[1:]), '/#convenios', reverse('reference'))
        for route in public_routes:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                main_nav = response.content.decode().split('<nav id="main-nav"', 1)[1].split('</nav>', 1)[0]
                for link in main_links:
                    self.assertIn(f'href="{link}"', main_nav)
                self.assertNotContains(response, 'class="account-nav"')
                self.assertNotContains(response, 'class="account-menu"')
                self.assertNotContains(response, 'nav-toggle')
                self.assertNotContains(response, 'nav-more')
        self.client.force_login(self.family)
        for route in ('home', 'explore', 'plans', 'organizations'):
            with self.subTest(client_route=route):
                response = self.client.get(reverse(route))
                for business_link in ('providers', 'relief_home', 'register_provider', 'management'):
                    path = reverse(business_link, args=['activities'] if business_link == 'management' else [])
                    self.assertNotContains(response, f'href="{path}"')
                self.assertNotContains(response, 'class="account-nav"')
                self.assertContains(response, '<details class="account-menu">')
        for route in ('public_landing', 'providers', 'relief_home'):
            self.assertRedirects(self.client.get(reverse(route)), reverse('home'))
        for route in ('dashboard', 'bookings', 'requests', 'profile', 'wallet'):
            response = self.client.get(reverse(route))
            self.assertContains(response, '<details class="account-menu">')
            self.assertNotContains(response, 'class="account-nav"')
        self.assertContains(self.client.get(reverse('activity', args=[self.activity.pk])), '<details class="account-menu">')

    def test_account_dropdown_keeps_each_roles_links_and_profile_labels(self):
        users = (
            (self.family, ('Perfil', 'Favoritos', 'Sparks'), ('Estadísticas', 'Usuarios y permisos', 'Publicaciones')),
            (m.User.objects.get(username='proveedor'), ('Perfil', 'Publicaciones', 'Horarios y cupos'), ('Estadísticas', 'Usuarios y permisos')),
            (m.User.objects.get(username='superadmin'), ('Perfil', 'Estadísticas', 'Usuarios y permisos', 'Validación de proveedores'), ()),
            (m.User.objects.create_user('nuevo_proveedor', email='alta@example.invalid', provider_applicant=True),
             ('Mis fichas',), ('Reservas', 'Estadísticas', 'Publicaciones')),
        )
        for user, required, restricted in users:
            with self.subTest(role=user.role):
                self.client.force_login(user)
                content = self.client.get(reverse('explore')).content.decode()
                menu = content.split('<nav class="account-menu-items"', 1)[1].split('</nav>', 1)[0]
                self.assertIn('Configuración de perfil', menu)
                self.assertIn(f'<form method="post" action="{reverse("logout")}">', menu)
                for label in required:
                    self.assertIn(f'{label}</a>', menu)
                for label in restricted:
                    self.assertNotIn(f'{label}</a>', menu)

    def test_admin_navigation_keeps_catalogs_and_bell_up_top_and_operations_in_sidebar(self):
        self.login_profile('admin')
        admin = m.User.objects.get(username='admin')
        admin.notifications.create(kind=m.Notification.Kind.RESERVED, message='Aviso de prueba')
        categories = reverse('management', args=['categories'])
        edit = reverse('edit_record', args=['categories', self.activity.category_id])
        for url, group, current_link in (
            (reverse('platform_statistics'), 'Operación', reverse('platform_statistics')),
            (reverse('bookings'), 'Operación', reverse('bookings')),
            (categories, 'Gestión de datos', categories),
            (edit, 'Gestión de datos', categories),
            (reverse('profile'), 'Cuenta', reverse('profile')),
            (reverse('notifications'), 'Operación', None),
        ):
            with self.subTest(url=url):
                page = self.client.get(url)
                self.assertNotContains(page, 'class="account-menu"')
                self.assertNotContains(page, 'class="module-nav"')
                self.assertContains(page, 'id="workspace-links"')
                self.assertContains(page, 'aria-controls="workspace-links"')
                document = page.content.decode()
                main = document.split('<nav id="main-nav"', 1)[1].split('</nav>', 1)[0]
                header_account = document.split('<div class="account-links">', 1)[1].split('</header>', 1)[0]
                side = document.split('<nav id="workspace-links"', 1)[1].split('</nav>', 1)[0]
                self.assertEqual(main.count('<a '), 2)
                for name in ('explore', 'relief_home'):
                    self.assertIn(f'href="{reverse(name)}"', main)
                    self.assertNotIn(f'href="{reverse(name)}"', side)
                for name in ('platform_operations', 'platform_statistics', 'bookings', 'notifications'):
                    self.assertNotIn(f'href="{reverse(name)}"', main)
                for kind in ('organizations', 'activities', 'schedules', 'categories', 'cities', 'plans'):
                    self.assertIn(f'href="{reverse("management", args=[kind])}"', side)
                for name in ('platform_statistics', 'bookings', 'profile', 'requests'):
                    self.assertIn(f'href="{reverse(name)}"', side)
                self.assertNotIn(f'href="{reverse("notifications")}"', side)
                self.assertIn(f'href="{reverse("notifications")}"', header_account)
                self.assertIn('aria-label="Notificaciones, 1 sin leer"', header_account)
                if url == reverse('notifications'):
                    self.assertIn(f'href="{url}" aria-current="page"', header_account)
                self.assertIn(f'action="{reverse("logout")}"', side)
                self.assertNotIn('Reputación', side)
                self.assertEqual(side.count('<details class="ks-workspace-group"'), 3)
                self.assertEqual(side.count('<details class="ks-workspace-group" open>'), 1)
                active_group = side.split('<details class="ks-workspace-group" open>', 1)[1].lstrip()
                self.assertTrue(active_group.startswith(f'<summary>{group} '))
                if current_link:
                    self.assertIn(f'href="{current_link}" aria-current="page"', active_group.split('</details>', 1)[0])

    def test_provider_sidebar_persists_across_dashboard_tables_and_forms(self):
        self.login_profile('proveedor')
        schedule_list = reverse('management', args=['schedules'])
        edit = reverse('edit_record', args=['schedules', self.activity.schedules.get().pk])
        for url in (reverse('dashboard'), schedule_list, edit):
            with self.subTest(url=url):
                page = self.client.get(url)
                self.assertContains(page, 'id="workspace-links"')
                self.assertContains(page, 'class="account-menu"')
                self.assertNotContains(page, 'class="module-nav"')
                if url != reverse('dashboard'):
                    self.assertContains(page, f'href="{schedule_list}" aria-current="page"')

    def test_client_home_lists_only_own_future_bookings_without_attendance(self):
        landing = self.client.get(reverse('home'))
        self.assertTemplateUsed(landing, 'portal/home.html')
        self.assertContains(landing, 'Incorporar mi centro')
        slot = self.activity.schedules.get()
        booking = m.Booking.objects.create(user=self.family, schedule=slot, sparks=4, amount=0)
        m.Booking.objects.create(user=self.family, schedule=slot, sparks=4, amount=0, attendance_recorded=True)
        m.Booking.objects.create(user=self.family, schedule=slot, sparks=4, amount=0, status='cancelled')
        admin = m.User.objects.get(username='admin')
        m.Booking.objects.create(user=admin, schedule=slot, sparks=4, amount=0)
        self.login_profile('usuario')
        home = self.client.get(reverse('home'))
        self.assertTemplateUsed(home, 'portal/client_home.html')
        self.assertEqual(list(home.context['upcoming']), [booking])
        self.assertContains(home, 'Mis favoritos')
        self.assertNotContains(home, 'Incorporar mi centro')
        self.client.force_login(admin)
        self.assertRedirects(self.client.get(reverse('home')), reverse('platform_statistics'))
        self.client.force_login(m.User.objects.get(username='proveedor'))
        self.assertRedirects(self.client.get(reverse('home')), reverse('dashboard'))
        self.client.force_login(m.User.objects.get(username='superadmin'))
        self.assertRedirects(self.client.get(reverse('home')), reverse('superadmin:index'))

    def test_password_change_is_available_from_profile_settings_for_each_role(self):
        settings_url = reverse('profile')
        password_url = reverse('password_change')
        for username in ('usuario', 'proveedor', 'admin', 'superadmin'):
            with self.subTest(username=username):
                self.client.force_login(m.User.objects.get(username=username))
                panel = self.client.get(reverse('dashboard'), follow=True)
                self.assertNotContains(panel, f'href="{password_url}"')
                settings = self.client.get(settings_url)
                self.assertContains(settings, 'Configuración de perfil')
                self.assertContains(settings, f'href="{password_url}"')
                password = self.client.get(password_url)
                self.assertContains(password, 'Volver a Configuración de perfil')

        self.client.logout()
        self.login_profile('usuario')
        new_password = 'Prueba-Unica-De-Clave!508'
        response = self.client.post(password_url, {
            'old_password': 'usuario', 'new_password1': new_password, 'new_password2': new_password,
        }, follow=True)
        self.assertRedirects(response, settings_url)
        self.assertContains(response, 'class="ks-feedback is-success" role="status"')
        self.assertContains(response, 'Tu contraseña se actualizó.')
        self.family.refresh_from_db()
        self.assertTrue(self.family.check_password(new_password))
        self.assertEqual(self.client.get(settings_url).status_code, 200)

    def test_reservation_feedback_and_confirmation_are_contextual(self):
        self.client.force_login(self.family)
        slot = self.activity.schedules.get()
        activity = self.client.get(reverse('activity', args=[self.activity.pk]))
        self.assertContains(activity, 'data-confirm-title="Confirmar reserva"')
        self.assertContains(activity, 'aria-labelledby="confirm-dialog-title"')
        failed = self.client.post(reverse('reserve', args=[slot.pk]), follow=True)
        self.assertContains(failed, 'class="ks-feedback is-error" role="alert"')
        self.assertContains(failed, 'No tienes suficientes Sparks')
        self.assertFalse(self.family.bookings.exists())

    def test_client_cannot_submit_business_requests_or_register_an_organization(self):
        ally = m.Organization.objects.create(
            name='Aliado de prueba', city=self.center.city, kind='ally',
            created_by=self.family, approved=True,
        )
        old = m.ServiceRequest.objects.create(
            user=self.family, kind='advice', subject='Solicitud anterior', organization=ally,
        )
        self.login_profile('usuario')
        listing = self.client.get(reverse('requests'))
        self.assertContains(listing, old.subject)
        self.assertNotContains(listing, 'Nueva solicitud')
        self.assertNotContains(listing, 'Mis fichas')
        self.assertContains(self.client.get(reverse('request_detail', args=[old.pk])), old.subject)
        for route, args in [('organization_register', []), ('provider_submissions', []),
                            ('relief_advice', [ally.pk]), ('relief_quote', [ally.pk]), ('relief_diagnosis', [])]:
            url = reverse(route, args=args)
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, {'kind': 'agreement'}).status_code, 403)
        url = reverse('request_create')
        for kind in ('demo', 'advice', 'quote', 'diagnosis'):
            self.assertEqual(self.client.get(url, {'kind': kind}).status_code, 403)
            self.assertEqual(self.client.post(url, {'kind': kind}).status_code, 403)
        self.assertNotContains(self.client.get(url), 'Asesoría')
        self.assertEqual(m.ServiceRequest.objects.filter(user=self.family).count(), 1)
        business = self.client.post(url, {
            'kind': 'agreement', 'organization': ally.pk, 'entity_name': 'Colegio ficticio',
            'subject': 'Convenio', 'message': 'Consulta sobre el programa.',
        })
        agreement = m.ServiceRequest.objects.get(user=self.family, kind='agreement')
        self.assertIsNone(agreement.organization_id)
        self.assertRedirects(business, reverse('request_detail', args=[agreement.pk]))
        self.assertRedirects(self.client.get(reverse('register_provider')), reverse('home'))
        self.family.refresh_from_db()
        self.assertEqual(self.family.role, 'client')

    def test_platform_statistics_link_and_direct_access_match_role(self):
        endpoint = reverse('platform_statistics')
        self.assertRedirects(self.client.get(endpoint), f"{reverse('login')}?next={endpoint}")
        for username, can_view in [('admin', True), ('superadmin', True), ('usuario', False), ('proveedor', False)]:
            with self.subTest(username=username):
                self.client.force_login(m.User.objects.get(username=username))
                dashboard = self.client.get(reverse('dashboard'), follow=True)
                response = self.client.get(endpoint)
                if can_view:
                    self.assertContains(dashboard, f'href="{endpoint}"')
                    self.assertContains(response, 'Estadísticas de la plataforma')
                    self.assertContains(response, 'aria-current="page"')
                else:
                    self.assertNotContains(dashboard, f'href="{endpoint}"')
                    self.assertEqual(response.status_code, 403)

    def test_platform_statistics_use_saved_records_and_respect_dates(self):
        slot = self.activity.schedules.get()
        include = [m.Booking.objects.create(
            user=self.family, schedule=slot, sparks=4, amount=0, status=status,
        ) for status in ('reserved', 'cancelled')]
        outside = m.Booking.objects.create(
            user=self.family, schedule=slot, sparks=4, amount=0, attendance_recorded=True,
        )
        day = timezone.localdate()
        noon = timezone.make_aware(datetime.combine(day, datetime.min.time()).replace(hour=12))
        m.Booking.objects.filter(pk__in=[row.pk for row in include]).update(created_at=noon)
        m.Booking.objects.filter(pk=outside.pk).update(created_at=noon - timedelta(days=2))
        ticket = m.ServiceRequest.objects.create(
            user=self.family, kind='agreement', entity_name='Centro privado demo',
            subject='Asunto confidencial de prueba', message='Texto privado de la solicitud',
            status='reviewing',
        )
        m.ServiceRequest.objects.filter(pk=ticket.pk).update(created_at=noon)
        future = timezone.now() + timedelta(days=1)
        m.Schedule.objects.filter(pk=slot.pk).update(starts_at=future, capacity=10, available=6)
        m.Schedule.objects.create(activity=self.other_activity, starts_at=future, capacity=6, available=6)
        m.Schedule.objects.create(activity=self.activity, starts_at=future, active=False, capacity=20, available=0)
        m.Schedule.objects.create(activity=self.activity, starts_at=noon - timedelta(days=1), capacity=20, available=0)
        hidden = m.Activity.objects.create(
            organization=self.center, name='Fuera del catálogo', category=self.activity.category, active=False,
        )
        m.Schedule.objects.create(activity=hidden, starts_at=future, capacity=20, available=0)

        self.client.force_login(m.User.objects.get(username='admin'))
        response = self.client.get(reverse('platform_statistics'), {'from': day.isoformat(), 'to': day.isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['booking_count'], 2)
        self.assertEqual(dict(response.context['bookings_by_status']),
                         {'Reservado': 1, 'Cancelado': 1})
        self.assertEqual(dict(response.context['requests_by_status'])['En revisión'], 1)
        self.assertEqual(response.context['published_count'], 2)
        self.assertEqual(response.context['provider_count'], 2)
        self.assertEqual(response.context['open_request_count'], 1)
        self.assertEqual([row['count'] for row in response.context['timeline']['days']], [1])
        self.assertEqual(response.context['cities'], [(self.center.city.name, 1)])
        self.assertEqual(response.context['capacity'], {'slots': 2, 'seats': 16, 'available': 12, 'used': 4})
        self.assertContains(response, '<strong>25%</strong>', html=True)
        self.assertNotContains(response, ticket.subject)
        self.assertNotContains(response, 'Usuarios registrados')
        history = self.client.get(reverse('platform_statistics'))
        self.assertEqual(history.context['booking_count'], 3)
        self.assertEqual(history.context['completed_count'], 1)
        self.assertEqual(history.context['capacity'], response.context['capacity'])
        self.assertContains(history, '<dd>33%</dd>', html=True)

    def test_platform_statistics_marks_empty_rates_as_unavailable(self):
        m.Schedule.objects.update(active=False)
        self.client.force_login(m.User.objects.get(username='admin'))
        response = self.client.get(reverse('platform_statistics'))
        self.assertContains(response, 'Sin reservas para comparar por comuna.')
        self.assertContains(response, 'Sin horarios futuros publicados.')
        self.assertContains(response, '<span class="ks-stats-no-rate">Sin reservas</span>', html=True)


class ReliefTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo', stdout=StringIO())
        cls.requester = m.User.objects.get(username='proveedor')
        cls.family = m.User.objects.get(username='usuario')
        cls.admin = m.User.objects.get(username='admin')
        cls.ally = m.Organization.objects.get(origin_key='ally:ContaPyme Valparaíso')
        cls.unrelated = m.Organization.objects.get(origin_key='demo:operator-center')

    def test_reference_directory_contains_eight_classified_allies_and_filters(self):
        home = reverse('relief_home')
        directory = self.client.get(home)
        self.assertContains(directory, 'Cinco áreas de apoyo')
        self.assertContains(directory, 'Mis solicitudes')
        self.assertEqual(len(directory.context['allies']), 8)
        self.assertContains(directory, 'F29')
        self.assertNotContains(directory, 'Técnicos verificados')
        response = self.client.get(home, {'area': 'insurance'})
        self.assertEqual([entry['organization'].name for entry in response.context['allies']],
                         ['Previene Kids', 'Red Segura Marga Marga'])
        self.assertContains(response, 'aria-current="true"')
        self.assertNotContains(response, self.ally.name)
        self.assertContains(self.client.get(reverse('organizations') + '?kind=ally'), 'Diagnóstico rápido')

    def test_diagnostic_suggests_only_selected_supported_topics(self):
        response = self.client.get(reverse('relief_home'), {
            'diagnostico': '1', 'need': ['maintenance', 'insurance', 'legal', 'invalid'],
        })
        self.assertEqual({area['key'] for area in response.context['suggestions']}, {'maintenance', 'legal'})
        self.assertContains(response, 'Empieza por estas áreas')
        self.assertFalse(m.ServiceRequest.objects.exists())

    def request_data(self):
        return {
            'entity_name': 'Mi centro ficticio', 'relief_topic': 'tax', 'message': 'Necesidad de contabilidad',
            'preferred_city': self.ally.city_id, 'relief_channel': 'phone',
            'preferred_date': (timezone.localdate() + timedelta(days=3)).isoformat(), 'preferred_time': '11:30',
        }

    def test_quote_and_guidance_keep_preferences_and_private_followup(self):
        quote = reverse('relief_quote', args=[self.ally.pk])
        self.assertRedirects(self.client.get(quote), f"{reverse('login')}?next={quote}")
        self.client.force_login(self.requester)
        self.assertContains(self.client.get(quote), 'no confirma una cita')
        response = self.client.post(quote, self.request_data())
        order = m.ServiceRequest.objects.get(user=self.requester, kind='quote')
        detail = reverse('request_detail', args=[order.pk])
        self.assertRedirects(response, detail)
        self.assertEqual(order.organization, self.ally)
        self.assertEqual(order.preferred_city, self.ally.city)
        self.assertEqual(order.relief_channel, 'phone')
        self.assertEqual(order.preferred_time.strftime('%H:%M'), '11:30')
        self.assertEqual(order.events.get().status, 'pending')
        self.assertContains(self.client.get(detail), 'Teléfono')
        self.assertContains(self.client.get(reverse('relief_home')), f'SOL-{order.pk}')

        response = self.client.post(reverse('relief_diagnosis'), {
            **self.request_data(), 'relief_topic': 'orientation', 'message': 'Orientación para mi equipo',
        })
        orientation = m.ServiceRequest.objects.get(user=self.requester, kind='diagnosis')
        self.assertIsNone(orientation.organization)
        self.assertRedirects(response, reverse('request_detail', args=[orientation.pk]))

        self.client.force_login(self.family)
        self.assertEqual(self.client.get(detail).status_code, 404)
        self.assertRedirects(self.client.get(reverse('relief_home')), reverse('home'))
        self.client.force_login(self.admin)
        self.assertRedirects(self.client.post(detail, {'status': 'reviewing', 'note': 'Recibida para revisión'}), detail)
        self.assertContains(self.client.get(reverse('relief_home')), self.ally.name)
        self.client.force_login(self.requester)
        self.assertContains(self.client.get(detail), 'Recibida para revisión')

    def test_platform_admin_can_browse_and_filter_relief_but_cannot_submit(self):
        self.client.force_login(self.admin)
        home = reverse('relief_home')
        directory = self.client.get(home)
        self.assertContains(directory, self.ally.name)
        self.assertContains(directory, f'href="{home}" aria-current="page">Alivios B2B')
        for label in ('Diagnóstico rápido', 'Solicitar asesoría', 'Cotizar con', 'Mis solicitudes'):
            self.assertNotContains(directory, label)
        filtered = self.client.get(home, {'area': 'insurance'})
        self.assertContains(filtered, 'Previene Kids')
        self.assertNotContains(filtered, self.ally.name)

        for route, args in (('relief_diagnosis', []), ('relief_quote', [self.ally.pk]), ('relief_advice', [self.ally.pk])):
            with self.subTest(route=route):
                url = reverse(route, args=args)
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(self.client.post(url, self.request_data()).status_code, 403)
        self.assertFalse(m.ServiceRequest.objects.exists())

    def test_advice_rejects_invalid_preferences_and_never_routes_to_an_unpublished_ally(self):
        self.client.force_login(self.requester)
        payload = self.request_data()
        advice = reverse('relief_advice', args=[self.ally.pk])
        self.assertEqual(self.client.post(reverse('relief_advice', args=[self.unrelated.pk]), payload).status_code, 404)
        response = self.client.post(advice, {
            **payload, 'preferred_date': (timezone.localdate() - timedelta(days=1)).isoformat(),
            'relief_channel': 'invalid',
        })
        self.assertContains(response, 'La fecha no puede estar en el pasado.')
        self.assertFalse(m.ServiceRequest.objects.exists())
        response = self.client.post(advice, {**payload, 'organization': self.unrelated.pk, 'kind': 'diagnosis'})
        request = m.ServiceRequest.objects.get(user=self.requester, kind='advice', organization=self.ally)
        self.assertRedirects(response, reverse('request_detail', args=[request.pk]))
        m.Organization.objects.filter(pk=self.ally.pk).update(active=False)
        self.assertEqual(self.client.post(advice, payload).status_code, 404)
        self.assertEqual(m.ServiceRequest.objects.count(), 1)


class PortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = m.User.objects.create_user('familia', email='familia@example.invalid', password='Family-Example!59', credits=26)
        cls.other = m.User.objects.create_user('otra', email='otra@example.invalid', password='Other-Example!59')
        cls.manager = m.User.objects.create_user('gestor', email='gestor@example.invalid', password='Manager-Example!59', is_staff=True)
        cls.manager.user_permissions.set(Permission.objects.filter(content_type__app_label='core').exclude(content_type__model='user'))
        cls.root = m.User.objects.create_superuser('super', 'super@example.invalid', 'Root-Example!59')
        cls.city, _ = m.City.objects.get_or_create(name='Valparaíso')
        cls.cat, _ = m.Category.objects.get_or_create(name='Deportes')
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

    def test_plan_cards_sort_active_plans_by_price_and_keep_integral_recommended(self):
        self.plan.origin_key = 'plan:Integral'
        self.plan.save(update_fields=['origin_key'])
        m.Plan.objects.create(name='Full Spark', origin_key='plan:Full Spark', sparks=34, price=45499)
        m.Plan.objects.create(name='Explorador', origin_key='plan:Explorador', sparks=15, price=24990)
        m.Plan.objects.create(name='Plan Complementario', sparks=40, price=27990, description='Nuevo en el catálogo.')
        m.Plan.objects.create(name='Esencial', sparks=10, price=27990)
        m.Plan.objects.create(name='Oculto', sparks=5, price=1, active=False)

        response = self.client.get(reverse('plans'))

        self.assertEqual(
            [card['name'] for card in response.context['cards']],
            ['Plan Explorador', 'Plan Esencial', 'Plan Complementario', 'Plan Integral', 'Plan Full Spark'],
        )
        self.assertContains(response, f'class="ks-plan ks-plan-recommended" aria-labelledby="plan-{self.plan.pk}"')
        self.assertContains(response, 'class="ks-plan-badge"', count=1)
        self.assertContains(response, '$34.990 CLP')
        self.assertContains(response, '350 Spark Points iniciales demo')
        self.assertContains(response, 'Nuevo en el catálogo.')
        self.assertNotContains(response, 'Plan Oculto')
        self.assertContains(response, f'href="{reverse("login")}?next={reverse("plans")}"', count=5)

    def test_plan_choice_preserves_demo_confirmation_and_credits(self):
        self.auth()
        plans_page = self.client.get(reverse('plans'))
        activate = reverse('activate_plan', args=[self.plan.pk])
        self.assertContains(plans_page, f'method="post" action="{activate}"')
        self.assertContains(plans_page, 'data-confirm-label="Activar plan demo"')
        self.assertContains(plans_page, 'Elegir plan')

        self.assertRedirects(self.client.post(activate), reverse('wallet'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.credits, 52)
        self.assertEqual(m.Membership.objects.get(user=self.user, plan=self.plan).sparks, 26)

    def test_local_visual_resources_resolve(self):
        from django.contrib.staticfiles import finders
        for path in ['logo.png', 'css/styles.css', 'portal.css', 'portal-theme.css', 'portal-icons.svg', 'catalog-map.svg',
                     'portal.js', 'landing.css', 'landing.js', 'taller-robotica.jpg', 'admin/css/base.css']:
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

    def test_landing_keeps_filtered_catalog_links_and_scopes_visual_resources(self):
        explore = reverse('explore')
        public_home = self.client.get(reverse('home'))
        self.assertContains(public_home, 'Escena ilustrativa')
        self.assertContains(public_home, 'id="convenios"')
        for query in ('Rob%C3%B3tica', 'Jiu-Jitsu', 'Nataci%C3%B3n', 'Piano'):
            self.assertContains(public_home, f'href="{explore}?q={query}"')

        self.auth()
        client_home = self.client.get(reverse('home'))
        self.assertTemplateUsed(client_home, 'portal/client_home.html')
        for resource in ('landing.css', 'landing.js', 'taller-robotica.jpg'):
            self.assertContains(public_home, f'/static/{resource}')
            self.assertNotContains(client_home, f'/static/{resource}')

    def test_catalog_period_availability_and_map_use_the_same_filtered_set(self):
        vina = m.City.objects.create(name='Viña del Mar')
        self.foreign_org.city = vina
        self.foreign_org.save(update_fields=['city'])
        now = timezone.make_aware(datetime(2030, 5, 6, 8))
        for activity, day, hour, capacity in (
            (self.activity, 7, 10, 0),
            (self.activity, 7, 17, 3),
            (self.activity, 8, 10, 2),
            (self.foreign_activity, 11, 10, 4),
        ):
            m.Schedule.objects.create(
                activity=activity, starts_at=timezone.make_aware(datetime(2030, 5, day, hour)),
                capacity=max(1, capacity), available=capacity,
            )
        endpoint = reverse('explore')
        with patch('core.views.timezone.now', return_value=now):
            response = self.client.get(endpoint, {
                'q': self.cat.name, 'age': '8-10', 'period': 'morning', 'sparks': 4, 'available': 1,
            })
            self.assertEqual(response.status_code, 200)
            result, = response.context['page'].object_list
            self.assertEqual(result.pk, self.activity.pk)
            self.assertEqual(result.catalog_cupos, 2)
            self.assertEqual(timezone.localtime(result.catalog_next).day, 8)
            self.assertEqual(
                {point['city'].name: point['count'] for point in response.context['map_points']},
                {self.city.name: 1, vina.name: 0},
            )
            self.assertContains(response, 'Mapa referencial por comuna')
            self.assertContains(response, 'period=morning&amp;sparks=4&amp;available=1&amp;city=')

            response = self.client.get(endpoint, {'city': vina.pk, 'period': 'weekend'})
            self.assertEqual([item.pk for item in response.context['page']], [self.foreign_activity.pk])
            self.assertContains(response, 'aria-current="location"')
            self.assertContains(response, f'href="#actividad-{self.foreign_activity.pk}"')

            response = self.client.get(endpoint, {'city': self.city.pk, 'period': 'after-school'})
            self.assertEqual(response.context['page'][0].catalog_cupos, 3)
            response = self.client.get(endpoint, {'city': vina.pk, 'period': 'morning'})
            self.assertContains(response, 'No encontramos coincidencias')

    def test_catalog_favorite_action_preserves_filters(self):
        self.auth()
        query = f'?city={self.city.pk}&age=8-10'
        favorite = reverse('favorite', args=[self.activity.pk])
        response = self.client.post(favorite + query, {'from_catalog': '1'})
        self.assertRedirects(response, reverse('explore') + query)
        response = self.client.get(reverse('explore') + query + '&favorites=1')
        self.assertContains(response, 'aria-pressed="true"')
        self.assertEqual([item.pk for item in response.context['page']], [self.activity.pk])

    def test_dashboard_prioritizes_actions_for_each_role(self):
        dashboard = reverse('dashboard')
        offer = reverse('management', args=['activities'])
        capacity = reverse('management', args=['schedules'])
        review = reverse('provider_review_queue')
        self.auth()
        family = self.client.get(dashboard)
        self.assertContains(family, 'Mi panel de cliente')
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
        response = self.client.post('/registro/', {'username': 'nueva', 'email': 'NUEVA@example.invalid', 'password1': 'Safe-Demo-New!45', 'password2': 'Safe-Demo-New!45', 'is_staff': 'on', 'is_superuser': 'on', 'credits': 99999, 'provider_applicant': 'on'})
        self.assertEqual(response.status_code, 302)
        obj = m.User.objects.get(username='nueva')
        self.assertFalse(obj.is_staff)
        self.assertFalse(obj.is_superuser)
        self.assertEqual(obj.role, 'client')
        self.assertEqual(obj.credits, 0)
        self.assertTrue(obj.check_password('Safe-Demo-New!45'))
        self.assertNotEqual(obj.password, 'Safe-Demo-New!45')
        self.assertEqual(obj.email, 'nueva@example.invalid')

    def test_duplicate_email_rejected_case_insensitively(self):
        form = forms.RegisterForm({'username': 'dup', 'email': 'FAMILIA@example.invalid', 'password1': 'Safe-Demo-New!45', 'password2': 'Safe-Demo-New!45'})
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_registration_keeps_convenio_entry_and_rejects_external_return(self):
        registration = reverse('register')
        next_url = f"{reverse('request_create')}?kind=agreement"
        auth_page = self.client.get(reverse('login'), {'next': next_url})
        self.assertContains(auth_page, f'{registration}?next=%2Fsolicitudes%2Fnueva%2F%3Fkind%3Dagreement')
        self.assertContains(self.client.get(registration, {'next': next_url}), 'name="next"')
        details = {'password1': 'Unique-Safe-Demo!173', 'password2': 'Unique-Safe-Demo!173'}
        response = self.client.post(registration, {
            **details, 'username': 'cliente_nuevo', 'email': 'nuevo@example.invalid', 'next': next_url,
        })
        self.assertRedirects(response, next_url)
        self.client.logout()
        response = self.client.post(registration, {
            **details, 'username': 'cliente_dos', 'email': 'dos@example.invalid', 'next': 'https://example.invalid/',
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_logout_and_bad_password(self):
        self.assertFalse(self.client.login(username='familia', password='incorrect'))
        self.assertTrue(self.client.login(username='familia', password='Family-Example!59'))
        self.assertEqual(self.client.get('/panel/').status_code, 200)
        self.assertEqual(self.client.get('/salir/').status_code, 405)
        self.assertEqual(self.client.post('/salir/').status_code, 302)
        self.assertEqual(self.client.get('/panel/').status_code, 302)

    def test_all_user_and_admin_templates(self):
        self.auth()
        for url in ['/panel/', '/reservas/', '/solicitudes/', '/solicitudes/nueva/', '/mis-sparks/', '/cuenta/', '/cuenta/clave/']:
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
        self.assertEqual((self.user.credits, self.user.points, self.slot.available), (22, 0, 1))
        services.cancel(self.user, booking)
        with self.assertRaises(ValidationError):
            services.cancel(self.user, booking)
        self.user.refresh_from_db(); self.slot.refresh_from_db()
        self.assertEqual((self.user.credits, self.user.points, self.slot.available), (26, 0, 2))
        self.assertEqual(m.Movement.objects.filter(booking=booking).count(), 2)
        self.assertEqual(self.user.notifications.filter(booking=booking).count(), 2)

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
        self.assertFalse(self.user.notifications.exists())

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

    def test_last_seat_is_reserved_automatically_and_disappears_from_availability(self):
        self.slot.capacity = self.slot.available = 1
        self.slot.save()
        self.auth()
        reserve_url = reverse('reserve', args=[self.slot.pk])
        detail_url = reverse('activity', args=[self.activity.pk])
        self.assertContains(self.client.get(detail_url), f'action="{reserve_url}"')
        self.assertRedirects(self.client.post(reserve_url), reverse('bookings'))
        booking = self.user.bookings.get(schedule=self.slot)
        self.assertEqual(booking.status, m.Booking.Status.RESERVED)
        self.slot.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual((self.slot.available, self.user.credits, self.user.points), (0, 22, 0))
        self.assertNotContains(self.client.get(detail_url), f'action="{reserve_url}"')
        self.assertNotContains(self.client.get(reverse('explore'), {'available': '1'}), self.activity.name)
        self.assertRedirects(self.client.post(reserve_url), detail_url)
        self.assertEqual(self.user.notifications.count(), 1)
        services.cancel(self.user, booking)
        self.slot.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual((self.slot.available, self.user.credits, self.user.points), (1, 26, 0))

    def test_other_user_cannot_cancel_or_download(self):
        b = services.reserve(self.user, self.slot.pk)
        self.auth(self.other)
        self.assertEqual(self.client.post(f'/reservas/{b.pk}/cancel/').status_code, 404)
        self.assertEqual(self.client.get(f'/comprobantes/{b.pk}/').status_code, 404)

    def test_schedule_cancellation_at_48_hours_refunds_and_notifies_each_customer(self):
        self.other.credits = 10
        self.other.save(update_fields=['credits'])
        bookings = [services.reserve(user, self.slot.pk) for user in (self.user, self.other)]
        soon = timezone.now() + timedelta(days=3)
        unaffected = m.Schedule.objects.create(activity=self.activity, starts_at=soon, capacity=2, available=2)
        reason = 'El recinto estará cerrado por mantención.'
        url = reverse('cancel_schedule', args=[self.slot.pk])
        self.auth(self.manager)
        listing = self.client.get(reverse('management', args=['schedules']))
        self.assertContains(listing, url)
        self.assertContains(self.client.get(url), 'Motivo de la cancelación')
        exact_cutoff = self.slot.starts_at - timedelta(hours=48)
        with patch('core.services.timezone.now', return_value=exact_cutoff):
            self.assertRedirects(self.client.post(url, {'reason': reason}), reverse('management', args=['schedules']))
        self.slot.refresh_from_db()
        unaffected.refresh_from_db()
        self.assertEqual((self.slot.active, self.slot.cancellation_reason, self.slot.available), (False, reason, 2))
        self.assertTrue(unaffected.active)
        self.assertEqual(self.slot.cancelled_at, exact_cutoff)
        self.assertContains(self.client.post(url, {'reason': 'Reintento'}), 'Solo puedes cancelar')
        self.assertEqual(self.client.get(reverse('edit_record', args=['schedules', self.slot.pk])).status_code, 403)

        for booking, credits in zip(bookings, (26, 10)):
            booking.refresh_from_db()
            self.assertEqual(booking.status, m.Booking.Status.CANCELLED)
            self.assertEqual(booking.user.credits, credits)
            self.assertEqual(list(m.Movement.objects.filter(booking=booking).order_by('pk').values_list('delta', flat=True)), [-4, 4])
            notice = booking.notification_set.get(kind=m.Notification.Kind.SCHEDULE_CANCELLED)
            self.assertEqual(notice.recipient_id, booking.user_id)
            self.assertIn(reason, notice.message)
        with self.assertRaises(ValidationError):
            services.reserve(self.user, self.slot.pk)

    def test_schedule_cancellation_requires_reason_scope_and_deadline_in_server(self):
        booking = services.reserve(self.user, self.slot.pk)
        url = reverse('cancel_schedule', args=[self.slot.pk])
        self.auth()
        self.assertEqual(self.client.post(url, {'reason': 'Intento de cliente'}).status_code, 403)
        self.auth(self.manager)
        foreign = m.Schedule.objects.create(activity=self.foreign_activity, starts_at=self.slot.starts_at, capacity=1, available=1)
        self.assertEqual(self.client.post(reverse('cancel_schedule', args=[foreign.pk]), {'reason': 'Otro centro'}).status_code, 404)
        self.assertContains(self.client.post(url, {'reason': '  '}), 'errorlist')
        self.assertEqual(self.client.post(reverse('deactivate', args=['schedules', self.slot.pk])).status_code, 403)
        edit = reverse('edit_record', args=['schedules', self.slot.pk])
        self.assertRedirects(self.client.post(edit, {
            'activity': self.activity.pk, 'starts_at': self.slot.starts_at.isoformat(),
            'capacity': self.slot.capacity,
        }), reverse('management', args=['schedules']))
        late = self.slot.starts_at - timedelta(hours=48) + timedelta(seconds=1)
        with patch('core.services.timezone.now', return_value=late):
            self.assertContains(self.client.post(url, {'reason': 'Fuera del plazo'}), 'al menos 48 horas')
        booking.refresh_from_db()
        self.slot.refresh_from_db()
        self.assertEqual(booking.status, m.Booking.Status.RESERVED)
        self.assertTrue(self.slot.active)
        self.assertIsNone(self.slot.cancelled_at)
        self.assertEqual(self.user.notifications.count(), 1)

    def test_schedule_cancellation_rolls_back_if_notification_cannot_be_saved(self):
        booking = services.reserve(self.user, self.slot.pk)
        with patch('core.services.notify_booking', side_effect=RuntimeError('Fallo de escritura')):
            with self.assertRaises(RuntimeError):
                services.cancel_schedule(self.manager, self.slot, 'Mantención.')
        booking.refresh_from_db()
        self.slot.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual((self.slot.active, self.slot.available, self.user.credits), (True, 1, 22))
        self.assertEqual(booking.status, m.Booking.Status.RESERVED)
        self.assertEqual(self.user.notifications.count(), 1)

    def test_schedule_cancellation_preserves_bookings_that_already_have_attendance(self):
        booking = services.reserve(self.user, self.slot.pk)
        services.complete(self.manager, booking)
        services.cancel_schedule(self.manager, self.slot, 'Cierre del recinto.')
        booking.refresh_from_db()
        self.user.refresh_from_db()
        self.assertTrue(booking.attendance_recorded)
        self.assertEqual((booking.status, self.user.credits, self.user.points), ('reserved', 22, 50))
        self.assertEqual(self.user.notifications.count(), 1)
        self.assertTrue(m.Settlement.objects.filter(booking=booking).exists())

    def test_notifications_are_private_and_read_actions_are_explicit(self):
        booking = services.reserve(self.user, self.slot.pk)
        mine = self.user.notifications.get()
        another = m.Notification.objects.create(
            recipient=self.other, kind=m.Notification.Kind.SCHEDULE_CANCELLED, message='Aviso privado de otro cliente.',
        )
        landing = reverse('notifications')
        read = reverse('read_notification', args=[mine.pk])
        self.assertRedirects(self.client.get(landing), f"{reverse('login')}?next={landing}")
        self.auth()
        response = self.client.get(landing)
        self.assertContains(response, 'Notificaciones, 1 sin leer')
        self.assertContains(response, f'/reservas/#reserva-{booking.pk}')
        self.assertNotContains(response, another.message)
        self.assertEqual(self.client.get(read).status_code, 405)
        self.assertEqual(self.client.post(reverse('read_notification', args=[another.pk])).status_code, 404)
        mine.refresh_from_db()
        self.assertIsNone(mine.read_at)
        self.assertRedirects(self.client.post(read), landing)
        mine.refresh_from_db()
        self.assertIsNotNone(mine.read_at)
        services.cancel(self.user, booking)
        self.assertEqual(self.user.notifications.filter(read_at__isnull=True).count(), 1)
        self.assertRedirects(self.client.post(reverse('read_all_notifications')), landing)
        another.refresh_from_db()
        self.assertIsNone(another.read_at)
        self.assertNotContains(self.client.get(landing), 'Notificaciones, 1 sin leer')

    def test_complete_once_and_financial_balance(self):
        b = services.reserve(self.user, self.slot.pk)
        self.auth(self.manager)
        self.assertEqual(self.client.post(f'/reservas/{b.pk}/complete/').status_code, 302)
        with self.assertRaises(ValidationError): services.complete(self.manager, b)
        self.assertEqual(services.available_balance(self.org), 25000)
        self.assertEqual(m.Settlement.objects.count(), 1)
        self.user.refresh_from_db()
        self.assertEqual(self.user.points, 50)

    def test_withdrawals_reserve_balance_and_reject_releases(self):
        b = services.reserve(self.user, self.slot.pk)
        services.complete(self.manager, b)
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
        self.other.provider_applicant = True
        self.other.save(update_fields=['provider_applicant'])
        self.auth(self.other)
        response = self.client.post('/solicitudes/nueva/', {'kind': 'advice', 'organization': self.ally.pk, 'entity_name': 'Centro ficticio', 'subject': 'Contabilidad', 'message': 'Necesito orientación.'})
        self.assertEqual(response.status_code, 302)
        obj = m.ServiceRequest.objects.get()
        self.assertEqual(obj.events.count(), 1)
        self.assertContains(self.client.get(f'/solicitudes/{obj.pk}/'), 'Necesito orientación.')
        self.auth()
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
        foreign = m.Schedule.objects.create(
            activity=self.foreign_activity, starts_at=self.slot.starts_at, capacity=5, available=4,
        )
        m.Booking.objects.create(user=self.manager, schedule=foreign, sparks=4, amount=10000)
        self.auth(self.manager)
        response = self.client.get('/panel/')
        self.assertEqual(response.context['summary']['counts']['total'], 1)
        self.assertEqual(response.context['summary']['counts']['booking_amount'], 25000)
        services.cancel(self.user, b)
        response = self.client.get('/panel/')
        self.assertEqual(response.context['summary']['counts']['booking_amount'], 0)
        self.assertEqual(response.context['summary']['counts']['total'], 1)

    def test_center_dashboard_metrics_match_the_admin_view_and_filter_by_ownership(self):
        first = services.reserve(self.user, self.slot.pk)
        services.complete(self.manager, first)
        m.Review.objects.create(booking=first, rating=5, comment='Muy bien.')
        another = m.Schedule.objects.create(
            activity=self.activity, starts_at=self.slot.starts_at + timedelta(days=1), capacity=4, available=4,
        )
        services.reserve(self.user, another.pk)
        to_cancel = m.Schedule.objects.create(
            activity=self.activity, starts_at=self.slot.starts_at + timedelta(days=2), capacity=2, available=2,
        )
        services.reserve(self.user, to_cancel.pk)
        services.cancel_schedule(self.manager, to_cancel, 'Cierre del recinto.')
        day = timezone.localdate()
        past = m.Booking.objects.create(user=self.other, schedule=another, sparks=4, amount=25000)
        m.Booking.objects.filter(pk=past.pk).update(created_at=timezone.now() - timedelta(days=1))
        filters = {
            'center': self.org.pk, 'activity': self.activity.pk, 'from': day.isoformat(), 'to': day.isoformat(),
        }

        self.auth(self.manager)
        dashboard = self.client.get(reverse('dashboard'), filters)
        self.assertContains(dashboard, 'Reservas por día y hora de la actividad')
        self.assertContains(dashboard, 'Navegación del tablero')
        self.assertContains(dashboard, 'Ver datos del gráfico')
        self.assertContains(dashboard, 'Cierre del recinto.')
        provider = dashboard.context['summary']
        self.assertEqual(
            {key: provider['counts'][key] for key in ('total', 'reserved', 'attended', 'center_cancelled', 'booking_amount')},
            {'total': 3, 'reserved': 2, 'attended': 1, 'center_cancelled': 1, 'booking_amount': 50000},
        )
        self.assertEqual((provider['prior_orders'], provider['families'], provider['returning'], provider['rating']), (1, 1, 1, 5))
        self.assertEqual(provider['heatmap']['peak'], 1)
        self.assertEqual([(row['count'], row['attended']) for row in provider['timeline']['days']], [(2, 1)])
        self.assertEqual(provider['timeline']['peak'], 2)
        self.assertEqual(self.client.get(reverse('dashboard'), {'center': self.foreign_org.pk}).status_code, 404)
        self.assertEqual(self.client.get(reverse('dashboard'), {'activity': self.foreign_activity.pk}).status_code, 404)
        self.assertEqual(self.client.get(reverse('platform_statistics'), filters).status_code, 403)
        exported = {**filters, 'export': 'workshops'}
        self.activity.name = '=Nombre con fórmula'
        self.activity.save(update_fields=['name'])
        provider_csv = self.client.get(reverse('dashboard'), exported)
        self.assertContains(provider_csv, "'=Nombre con fórmula,2,1,1,50000")
        self.assertNotContains(provider_csv, self.foreign_activity.name)

        self.auth(m.User.objects.get(username='admin'))
        mirror = self.client.get(reverse('platform_statistics'), filters)
        self.assertTemplateUsed(mirror, 'portal/provider_statistics.html')
        self.assertContains(mirror, 'Ver toda la plataforma')
        self.assertEqual(mirror.context['summary']['counts'], provider['counts'])
        self.assertEqual(self.client.get(reverse('platform_statistics'), exported).content, provider_csv.content)

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
        self.auth_applicant()
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
        self.auth_applicant()
        response = self.client.post(reverse('organization_register'), self.provider_payload())
        org = m.Organization.objects.get(name='Taller ficticio')
        self.assertRedirects(response, reverse('provider_submission', args=[org.pk]))
        return org

    def auth_applicant(self):
        self.user.provider_applicant = True
        self.user.save(update_fields=['provider_applicant'])
        self.auth()

    def review_provider(self, org, status, note):
        self.auth(self.root)
        url = reverse('provider_review', args=[org.pk])
        response = self.client.post(url, {
            'revision': org.review_events.first().pk, 'status': status, 'note': note,
        })
        self.assertRedirects(response, url)

    def test_public_provider_entry_continues_account_creation_to_intake(self):
        entry = reverse('providers')
        registration = reverse('register_provider')
        intake = reverse('organization_register')
        self.assertContains(self.client.get(entry), f'href="{registration}"')
        self.assertRedirects(self.client.get(reverse('provider_submissions')), f"{reverse('login')}?next={reverse('provider_submissions')}")
        self.assertRedirects(self.client.get(reverse('register'), {'next': intake}), registration)
        self.assertContains(self.client.get(registration), 'Crea tu cuenta de proveedor')
        response = self.client.post(registration, {
            'username': 'contacto-demo', 'email': 'contacto@example.invalid',
            'password1': 'Demo-Unique!9182', 'password2': 'Demo-Unique!9182',
            'is_staff': 'on', 'is_superuser': 'on',
        })
        self.assertRedirects(response, intake)
        applicant = m.User.objects.get(username='contacto-demo')
        self.assertEqual(applicant.role, 'applicant')
        self.assertEqual(self.client.get(reverse('management', args=['activities'])).status_code, 403)
        self.client.logout()
        self.assertRedirects(self.client.post(reverse('login'), {
            'username': applicant.username, 'password': 'Demo-Unique!9182',
        }), reverse('provider_submissions'))

    def test_provider_registration_requires_demo_acknowledgment_and_pilot_city(self):
        self.auth_applicant()
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
            services.reserve(self.other, slot.pk)

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
            listing = self.client.get(reverse('provider_submissions'))
            if user == self.other:
                self.assertEqual(listing.status_code, 403)
            else:
                self.assertNotContains(listing, org.name)
            self.assertEqual(self.client.get(owner_detail).status_code, 404)
            self.assertEqual(self.client.post(owner_detail, self.provider_payload()).status_code, 404)
            self.assertEqual(self.client.get(reverse('provider_review_queue')).status_code, 403)
            self.assertEqual(self.client.get(review).status_code, 403)
            self.assertEqual(self.client.post(review, {'status': 'approved'}).status_code, 403)
        self.assertEqual(org.review_events.count(), 1)

    def test_staff_cannot_complete_foreign_booking_even_as_owner(self):
        self.manager.credits = 20; self.manager.save()
        slot = m.Schedule.objects.create(activity=self.foreign_activity, starts_at=timezone.now() + timedelta(days=1), capacity=1, available=1)
        booking = m.Booking.objects.create(user=self.manager, schedule=slot, sparks=4, amount=0)
        self.auth(self.manager)
        self.assertEqual(self.client.post(f'/reservas/{booking.pk}/complete/').status_code, 403)

    def test_database_enforces_email_case_insensitive_uniqueness(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            m.User.objects.create_user('dup_case', email='FAMILIA@example.invalid')

    def test_export_respects_status_filter(self):
        booking = services.reserve(self.user, self.slot.pk)
        self.auth()
        self.assertNotContains(self.client.get('/reservas/exportar/?status=cancelled'), f'KS-{booking.pk}')
        self.assertContains(self.client.get('/reservas/exportar/?status=reserved'), 'Reservado')
