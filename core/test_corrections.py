from datetime import timedelta
from tempfile import TemporaryDirectory
from io import StringIO

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command, CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from . import access, metrics, models as m, services


class ProviderIntakeCorrectionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = m.User.objects.create_user('kids-new', email='kids-new@example.invalid', password='Academic-Only-Test-482!', provider_applicant=True)
        cls.admin = m.User.objects.get(username='admin')
        cls.outsider = m.User.objects.get(username='proveedor')
        cls.center = m.Organization.objects.create(
            name='Kids Demo', city=m.City.objects.first(), specialty=m.Category.objects.first(),
            created_by=cls.owner, email='kids@example.invalid',
        )
        m.ProviderReviewEvent.objects.create(organization=cls.center, actor=cls.owner, status='pending', note='Ficha demo')

    def decide(self, status):
        return self.client.post(reverse('provider_review', args=[self.center.pk]), {
            'revision': self.center.review_events.first().pk, 'status': status, 'note': 'Decisión de prueba',
        })

    def test_platform_admin_reviews_and_enables_only_the_owner_and_center(self):
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse('provider_review_queue')), 'Kids Demo')
        self.assertContains(self.client.get(reverse('management', args=['organizations'])), 'Solicitud recibida')
        self.assertEqual(self.decide('reviewing').status_code, 302)
        revision = self.center.review_events.first().pk
        self.assertEqual(self.decide('approved').status_code, 302)
        self.owner.refresh_from_db()
        self.center.refresh_from_db()
        self.assertEqual(self.owner.role, 'provider')
        self.assertTrue(self.owner.has_perm('core.add_activity'))
        self.assertFalse(self.owner.has_perm('core.operate_platform'))
        self.assertFalse(self.owner.has_perm('core.change_user'))
        self.assertEqual(list(access.organizations(self.owner)), [self.center])
        self.assertTrue(self.center.approved)
        self.assertTrue(m.AuditLog.objects.filter(actor=self.admin, action='provider_approved').exists())
        self.client.post(reverse('provider_review', args=[self.center.pk]), {
            'revision': revision, 'status': 'approved', 'note': 'Reintento',
        })
        self.assertEqual(self.center.review_events.count(), 3)
        self.client.force_login(self.owner)
        self.assertContains(self.client.get(reverse('provider_submission', args=[self.center.pk])), 'Abrir Seller Center')
        self.assertEqual(self.client.get(reverse('management', args=['activities'])).status_code, 200)

    def test_rejected_observed_and_unauthorized_decisions_do_not_grant_access(self):
        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get(reverse('provider_review_queue')).status_code, 403)
        with self.assertRaises(PermissionDenied):
            services.review_provider(self.owner, self.center, self.center.review_events.first().pk, 'reviewing', 'Intento')
        self.client.force_login(self.admin)
        self.decide('reviewing')
        self.decide('observed')
        self.owner.refresh_from_db()
        self.assertFalse(self.owner.is_staff)
        self.assertFalse(self.center.administrators.exists())
        self.assertEqual(self.center.review_events.first().status, 'observed')

    def test_legacy_approved_center_can_enable_owner_without_rewriting_history(self):
        self.center.approved = True
        self.center.save(update_fields=['approved'])
        self.client.force_login(self.admin)
        detail = reverse('provider_review', args=[self.center.pk])
        self.assertContains(self.client.get(detail), 'Habilitar acceso del titular')
        self.client.post(detail, {'action': 'enable'})
        self.client.post(detail, {'action': 'enable'})
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.role, 'provider')
        self.assertTrue(self.center.administrators.filter(pk=self.owner.pk).exists())
        self.assertEqual(self.center.review_events.count(), 1)
        self.assertEqual(m.AuditLog.objects.filter(action='provider_enabled', target=f'organization:{self.center.pk}').count(), 1)

    def approve(self):
        self.client.force_login(self.admin)
        self.decide('reviewing')
        self.decide('approved')
        self.owner.refresh_from_db()
        self.client.force_login(self.owner)

    def activity_payload(self, **updates):
        data = {
            'name': 'Matemáticas básicas', 'description': 'Actividad ficticia', 'organization': self.center.pk,
            'category': self.center.specialty_id, 'age_min': 5, 'age_max': 14, 'sparks': 4, 'price': 25000,
            'icon': '📚', 'modality': 'in_person', 'venue': 'Sala de demostración en Viña del Mar',
            'publication_status': 'published',
        }
        return {**data, **updates}

    def test_complete_new_provider_family_and_admin_journey(self):
        self.client.post(reverse('register_provider'), {
            'username': 'kids-flow', 'email': 'kids-flow@example.invalid',
            'password1': 'Academic-Only-Test-482!', 'password2': 'Academic-Only-Test-482!',
        })
        self.owner = m.User.objects.get(username='kids-flow')
        self.client.post(reverse('organization_register'), {
            'name': 'Kids Demo del recorrido', 'city': self.center.city_id, 'specialty': self.center.specialty_id,
            'description': 'Clases de matemáticas básicas', 'email': self.owner.email, 'phone': '000 000 000',
            'contact_first_name': 'Contacto', 'contact_last_name': 'Demo', 'demo_acknowledged': 'on',
        })
        self.center = m.Organization.objects.get(created_by=self.owner)
        self.assertFalse(self.owner.is_staff)
        self.assertFalse(self.center.approved)
        self.assertEqual(self.center.review_events.first().status, 'pending')
        self.approve()
        create = reverse('create_record', args=['activities'])
        response = self.client.post(create, self.activity_payload())
        activity = m.Activity.objects.get(name='Matemáticas básicas')
        sessions = reverse('management', args=['schedules']) + f'?activity={activity.pk}'
        self.assertRedirects(response, sessions)
        self.assertNotContains(self.client.get(reverse('explore')), activity.name)
        for days in (7, 14):
            response = self.client.post(reverse('create_record', args=['schedules']), {
                'activity': activity.pk, 'starts_at': timezone.now() + timedelta(days=days), 'capacity': 10, 'active': 'on',
            })
            self.assertEqual(response.status_code, 302)
        slot = activity.schedules.order_by('starts_at').first()
        self.client.logout()
        self.assertContains(self.client.get(reverse('explore'), {'q': activity.name, 'age': 8, 'city': self.center.city_id}), activity.name)
        self.assertTrue(self.client.login(username='usuario', password='usuario'))
        family = m.User.objects.get(username='usuario')
        plan = m.Plan.objects.create(name='Recarga de prueba', sparks=20)
        self.client.post(reverse('activate_plan', args=[plan.pk]))
        self.client.post(reverse('reserve', args=[slot.pk]))
        booking = m.Booking.objects.get(schedule=slot)
        slot.refresh_from_db()
        self.assertEqual(slot.available, 9)
        # A duplicate and a later login preserve exactly one reservation and one debit.
        self.client.post(reverse('reserve', args=[slot.pk]))
        self.client.logout()
        self.assertTrue(self.client.login(username='usuario', password='usuario'))
        self.assertContains(self.client.get(reverse('bookings')), f'KS-{booking.pk}')
        receipt = self.client.get(reverse('document', args=[booking.pk]))
        for expected in (self.center.name, 'America/Santiago', 'créditos simulados', 'No acredita pagos', 'Cupos: 1'):
            self.assertContains(receipt, expected)
        family.refresh_from_db()
        self.assertEqual(family.credits, 16)
        self.assertEqual(m.Movement.objects.filter(booking=booking).count(), 1)
        self.client.logout()
        self.assertTrue(self.client.login(username=self.owner.username, password='Academic-Only-Test-482!'))
        self.assertContains(self.client.get(reverse('bookings')), f'KS-{booking.pk}')
        self.assertContains(self.client.get(sessions), '9 / 10')
        self.assertContains(self.client.get(reverse('notifications')), f'KS-{booking.pk}')
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse('bookings'), {'center': self.center.pk}), f'KS-{booking.pk}')
        self.client.force_login(self.outsider)
        self.assertNotContains(self.client.get(reverse('bookings')), f'id="reserva-{booking.pk}"')
        self.assertNotContains(self.client.get(reverse('export_bookings')), f'KS-{booking.pk}')
        self.assertEqual(self.client.get(reverse('document', args=[booking.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse('management', args=['schedules']), {'activity': activity.pk}).status_code, 404)
        self.assertEqual(self.client.post(reverse('booking_action', args=[booking.pk, 'complete'])).status_code, 404)
        self.client.force_login(family)
        self.client.post(reverse('booking_action', args=[booking.pk, 'cancel']))
        slot.refresh_from_db()
        family.refresh_from_db()
        booking.refresh_from_db()
        self.assertEqual((slot.available, family.credits, booking.status), (10, 20, 'cancelled'))
        self.assertTrue(m.AuditLog.objects.filter(action='cancel', target=f'booking:{booking.pk}').exists())

    def test_publication_states_sold_out_and_form_rules(self):
        self.approve()
        create = reverse('create_record', args=['activities'])
        for updates, error in (({'age_min': 4}, 'age_min'), ({'age_max': 15}, 'age_max'), ({'venue': ''}, 'venue')):
            response = self.client.post(create, self.activity_payload(**updates))
            self.assertIn(error, response.context['form'].errors)
        response = self.client.post(create, self.activity_payload(publication_status='draft'))
        activity = m.Activity.objects.get(name='Matemáticas básicas')
        slot = m.Schedule.objects.create(activity=activity, starts_at=timezone.now() + timedelta(days=7), capacity=1, available=1)
        self.assertNotContains(self.client.get(reverse('explore')), activity.name)
        family = m.User.objects.get(username='usuario')
        with self.assertRaises(ValidationError):
            services.reserve(family, slot.pk)
        edit = reverse('edit_record', args=['activities', activity.pk])
        self.client.post(edit, self.activity_payload(publication_status='published'))
        self.assertContains(self.client.get(reverse('explore')), activity.name)
        with self.assertRaises(ValidationError):
            services.reserve(family, slot.pk)
        slot.refresh_from_db()
        self.assertEqual(slot.available, 1)
        m.User.objects.filter(pk=family.pk).update(credits=8)
        booking = services.reserve(family, slot.pk)
        self.assertNotContains(self.client.get(reverse('explore')), activity.name)
        another_center = m.Organization.objects.create(
            name='Otro centro propio', city=self.center.city, created_by=self.owner,
            email='other-owned@example.invalid', approved=True,
        )
        another_center.administrators.add(self.owner)
        moved = self.client.post(edit, self.activity_payload(organization=another_center.pk))
        self.assertIn('organization', moved.context['form'].errors)
        activity.refresh_from_db()
        self.assertEqual(activity.organization_id, self.center.pk)
        services.cancel(family, booking)
        self.assertContains(self.client.get(reverse('explore')), activity.name)
        self.client.post(reverse('deactivate', args=['activities', activity.pk]))
        activity.refresh_from_db()
        self.assertEqual(activity.publication_status, 'paused')
        self.assertNotContains(self.client.get(reverse('explore')), activity.name)

    def test_optional_uploaded_image_is_scoped_and_rejects_unsafe_formats(self):
        self.approve()
        with TemporaryDirectory() as folder, override_settings(MEDIA_ROOT=folder):
            bad = SimpleUploadedFile('image.svg', b'<svg onload="alert(1)"/>', content_type='image/svg+xml')
            response = self.client.post(reverse('create_record', args=['activities']), self.activity_payload(image=bad))
            self.assertIn('image', response.context['form'].errors)
            png = SimpleUploadedFile('illustration.png', b'\x89PNG\r\n\x1a\n' + b'\x00' * 20, content_type='image/png')
            self.client.post(reverse('create_record', args=['activities']), self.activity_payload(image=png, publication_status='draft'))
            activity = m.Activity.objects.get(name='Matemáticas básicas')
            image_url = reverse('activity_image', args=[activity.pk])
            response = self.client.get(image_url)
            self.assertEqual(response['Content-Type'], 'image/png')
            response.close()
            self.client.force_login(self.outsider)
            self.assertEqual(self.client.get(image_url).status_code, 404)
            self.client.logout()
            self.assertEqual(self.client.get(image_url).status_code, 404)


class DemoScenarioCorrectionsTests(TestCase):
    def load(self):
        call_command('seed_demo', scenario=True, stdout=StringIO())

    def test_scenario_is_repeatable_preserves_edits_and_has_coherent_balances(self):
        self.load()
        models = (m.User, m.Organization, m.Activity, m.Schedule, m.Booking, m.Review, m.Movement, m.Membership)
        counts = [model.objects.count() for model in models]
        activity = m.Activity.objects.get(origin_key='scenario:activity:0')
        activity.description = 'Edición humana conservada'
        activity.save(update_fields=['description'])
        self.load()
        activity.refresh_from_db()
        self.assertEqual(activity.description, 'Edición humana conservada')
        self.assertEqual(counts, [model.objects.count() for model in models])
        bookings = m.Booking.objects.filter(schedule__activity__demo_data=True)
        self.assertEqual(bookings.count(), 12)
        self.assertEqual(bookings.filter(attendance_recorded=True).count(), 4)
        self.assertEqual(bookings.filter(status='cancelled').count(), 2)
        self.assertEqual(m.Review.objects.filter(is_demo=True, booking__attendance_recorded=True).count(), 4)
        for slot in m.Schedule.objects.filter(activity__demo_data=True):
            occupied = slot.bookings.filter(status='reserved').count()
            self.assertEqual(slot.available, slot.capacity - occupied)
            self.assertGreaterEqual(slot.available, 0)
        for family in m.User.objects.filter(username__startswith='familia_demo_'):
            self.assertEqual(family.credits, sum(family.movements.values_list('delta', flat=True)))
            self.assertEqual(family.points, family.bookings.filter(points_awarded=True).count() * 50)
        self.assertEqual(set(m.Organization.objects.filter(origin_key__startswith='scenario:center:').values_list('city__name', flat=True)), set(m.City.PILOT))

    def test_scenario_metrics_reconcile_across_provider_admin_and_dates(self):
        self.load()
        aggregate = metrics.financial_reference(m.Booking.objects.all())
        total = 0
        gmv = 0
        for username in ('kidsdemo', 'robotica_demo'):
            owner = m.User.objects.get(username=username)
            self.client.force_login(owner)
            dashboard = self.client.get(reverse('dashboard'))
            total += dashboard.context['summary']['counts']['total']
            gmv += dashboard.context['financial']['gmv']
            self.assertContains(dashboard, 'Datos de demostración')
            self.assertContains(dashboard, 'Metas y proyección')
        self.client.force_login(m.User.objects.get(username='admin'))
        dashboard = self.client.get(reverse('platform_statistics'))
        self.assertEqual(total, dashboard.context['booking_count'])
        self.assertEqual(gmv, aggregate['gmv'])
        self.assertEqual(aggregate['gmv'], 250000)
        self.assertEqual(aggregate['estimated_commission'], 10000)
        recent = self.client.get(reverse('platform_statistics'), {'from': timezone.localdate().isoformat(), 'to': timezone.localdate().isoformat()})
        self.assertLess(recent.context['booking_count'], total)
        self.assertEqual(recent.context['financial']['estimated_commission'], 0)
        self.client.logout()
        activity = m.Activity.objects.get(origin_key='scenario:activity:0')
        self.assertContains(self.client.get(reverse('activity', args=[activity.pk])), 'Opinión ficticia')
        self.assertContains(self.client.get(reverse('activity', args=[activity.pk])), 'Demostración')

    def test_scenario_never_overwrites_colliding_accounts_and_rolls_back(self):
        existing = m.User.objects.create_user('kidsdemo', email='human-edit@example.invalid', first_name='Conservar')
        count = m.User.objects.count()
        with self.assertRaises(CommandError):
            self.load()
        existing.refresh_from_db()
        self.assertEqual(existing.first_name, 'Conservar')
        self.assertEqual(m.User.objects.count(), count)
        self.assertFalse(m.DemoScenario.objects.exists())
        self.assertFalse(m.Activity.objects.filter(demo_data=True).exists())

    @override_settings(KIDDO_ALLOW_DEMO_DATA=False)
    def test_scenario_is_denied_outside_explicit_demo_configuration(self):
        with self.assertRaises(CommandError):
            self.load()
        self.assertFalse(m.DemoScenario.objects.exists())
