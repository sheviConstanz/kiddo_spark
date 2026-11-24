from datetime import timedelta
from importlib import import_module
from io import StringIO
import os
from runpy import run_module
from unittest.mock import patch

from django.apps import apps
from django.core.management import call_command, CommandError
from django.db import connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.models.functions import TruncMonth
from django.test import SimpleTestCase, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from . import access, models as m, services
from .migrations import _defense_seed_v1 as seed


class DefenseSettingsTests(SimpleTestCase):
    def test_database_and_cookies_are_separate_from_normal_demo(self):
        with patch.dict(os.environ, {'KIDDO_DEFENSE_DB': 'defensa_test.sqlite3'}):
            config = run_module('kiddo.defense_settings')
        self.assertEqual(config['DATABASES']['default']['NAME'].parent.name, 'defense_data')
        self.assertFalse(config['KIDDO_SEED_DEMO_ACCOUNTS'])
        self.assertTrue(config['KIDDO_DEFENSE_DEMO'])
        self.assertEqual(config['SESSION_COOKIE_NAME'], 'kiddo_defense_session')

    def test_database_names_cannot_escape_the_dedicated_directory(self):
        from django.core.exceptions import ImproperlyConfigured
        for name in ('../kiddo.sqlite3', '/other.sqlite3', 'C:\\other.sqlite3', 'wrong.json'):
            with self.subTest(name=name), patch.dict(os.environ, {'KIDDO_DEFENSE_DB': name}):
                with self.assertRaises(ImproperlyConfigured):
                    run_module('kiddo.defense_settings')


class DefenseCollisionTests(TestCase):
    def test_colliding_account_is_preserved_and_failed_seed_rolls_back(self):
        account = m.User.objects.create_user('defensa_familia_01', email='kept-defense@example.invalid', credits=17)
        count = m.User.objects.count()
        with self.assertRaises(ValueError), transaction.atomic():
            seed.populate(apps, 'default')
        self.assertEqual(m.User.objects.count(), count)
        account.refresh_from_db()
        self.assertEqual(account.credits, 17)
        self.assertFalse(m.DemoScenario.objects.filter(key=seed.KEY).exists())


class DefenseDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        seed.populate(apps, 'default')
        cls.activities = m.Activity.objects.filter(origin_key__startswith=seed.PREFIX + 'activity:')
        cls.bookings = m.Booking.objects.filter(schedule__activity__in=cls.activities)

    def test_counts_types_history_reviews_and_month_of_available_activities(self):
        centers = m.Organization.objects.filter(origin_key__startswith=seed.PREFIX)
        self.assertEqual(centers.filter(approved=True).count(), 8)
        self.assertEqual(centers.filter(approved=False).count(), 3)
        self.assertEqual(self.activities.count(), 20)
        self.assertEqual(set(self.activities.values_list('organization__city__name', flat=True)), set(seed.CITIES))
        self.assertEqual(m.User.objects.filter(username__startswith='defensa_familia_').count(), 30)
        self.assertEqual(self.bookings.count(), 60)
        self.assertEqual(self.bookings.filter(attendance_recorded=True).count(), 26)
        self.assertEqual(self.bookings.filter(status='cancelled').count(), 7)
        reviews = m.Review.objects.filter(booking__in=self.bookings)
        self.assertEqual(reviews.count(), 15)
        self.assertFalse(reviews.exclude(booking__attendance_recorded=True, is_demo=True).exists())
        self.assertEqual(set(reviews.values_list('rating', flat=True)), {3, 4, 5})
        self.assertGreaterEqual(self.bookings.annotate(month=TruncMonth('created_at')).values('month').distinct().count(), 3)
        today = timezone.localdate()
        for activity in self.activities:
            future = activity.schedules.filter(starts_at__gt=timezone.now(), active=True, available__gt=0)
            self.assertEqual(future.count(), 15)
            last = timezone.localtime(future.latest('starts_at').starts_at).date()
            self.assertGreaterEqual(last, today + timedelta(days=29))
            self.assertLessEqual(last, today + timedelta(days=35))
        self.assertEqual(m.ServiceRequest.objects.filter(user__username__startswith='defensa_proveedor_', status='pending').count(), 3)

    def test_every_balance_seat_and_payment_reference_matches_the_ledger(self):
        for slot in m.Schedule.objects.filter(activity__in=self.activities):
            expected = slot.capacity - slot.bookings.filter(status='reserved').count()
            self.assertEqual(slot.available, expected)
            self.assertGreaterEqual(slot.available, 0)
            if slot.cancelled_at:
                self.assertFalse(slot.bookings.filter(status='reserved').exists())
                self.assertFalse(slot.active)
                self.assertTrue(slot.cancellation_reason)
        for family in m.User.objects.filter(username__startswith='defensa_familia_'):
            self.assertEqual(family.credits, sum(family.movements.values_list('delta', flat=True)))
            self.assertEqual(family.points, family.bookings.filter(points_awarded=True).count() * 50)
            self.assertGreaterEqual(family.credits, 0)
        for booking in self.bookings:
            self.assertEqual(booking.amount, booking.schedule.activity.price)
            self.assertEqual(booking.sparks, booking.schedule.activity.sparks)
            self.assertGreaterEqual(booking.created_at, booking.user.date_joined)
            if booking.attendance_recorded:
                self.assertLess(booking.schedule.starts_at, timezone.now())
                self.assertEqual(m.Settlement.objects.get(booking=booking).amount, booking.amount)

    def test_repetition_and_renewal_preserve_operations_and_extend_the_horizon(self):
        activity = self.activities.first()
        activity.description = 'Edición de presentación conservada'
        activity.save(update_fields=['description'])
        slots = list(m.Schedule.objects.filter(activity__in=self.activities).order_by('pk').values_list('pk', 'starts_at', 'available', 'active'))
        before = (m.User.objects.count(), m.Booking.objects.count(), m.Movement.objects.count(), m.Review.objects.count())
        self.assertFalse(seed.populate(apps, 'default'))
        self.assertEqual(seed.ensure_future_slots(apps, 'default'), 0)
        future_now = timezone.now() + timedelta(days=40)
        created = seed.ensure_future_slots(apps, 'default', future_now)
        self.assertEqual(created, 300)
        self.assertEqual(seed.ensure_future_slots(apps, 'default', future_now), 0)
        self.assertEqual(before, (m.User.objects.count(), m.Booking.objects.count(), m.Movement.objects.count(), m.Review.objects.count()))
        self.assertEqual(slots, list(m.Schedule.objects.filter(pk__in=[row[0] for row in slots]).order_by('pk').values_list('pk', 'starts_at', 'available', 'active')))
        activity.refresh_from_db()
        self.assertEqual(activity.description, 'Edición de presentación conservada')

    def test_same_booking_metrics_privacy_and_family_presentation(self):
        admin = m.User.objects.get(username='defensa_admin')
        owner = m.User.objects.get(username='defensa_proveedor_01')
        family = m.User.objects.get(username='defensa_familia_01')
        self.client.force_login(owner)
        report = self.client.get(reverse('dashboard'))
        self.assertEqual(report.context['summary']['counts']['total'], 28)
        self.assertEqual(len(report.context['summary']['workshops']), 4)
        self.assertEqual(report.context['summary']['counts']['attended'], 10)
        self.assertContains(self.client.get(reverse('reputation')), 'Demostración')
        total = 0
        for operator in m.User.objects.filter(username__startswith='defensa_proveedor_', is_staff=True):
            total += access.bookings(operator).count()
        self.assertEqual(total, 60)
        self.client.force_login(admin)
        stats = self.client.get(reverse('platform_statistics'))
        self.assertEqual(stats.context['booking_count'], 60)
        self.assertEqual(stats.context['provider_count'], 9)  # includes the original test fixture's center
        self.assertGreater(stats.context['financial']['estimated_commission'], 0)
        recent = self.client.get(reverse('platform_statistics'), {'from': timezone.localdate().isoformat()})
        self.assertLess(recent.context['booking_count'], 60)
        self.client.force_login(family)
        self.assertTrue(family.bookings.filter(attendance_recorded=True).exists())
        self.assertTrue(family.bookings.filter(schedule__starts_at__gt=timezone.now(), status='reserved').exists())
        self.assertGreaterEqual(m.Favorite.objects.filter(user=family).count(), 3)
        self.assertContains(self.client.get(reverse('home')), 'reservas')
        slot = services.bookable_schedules().filter(activity__in=self.activities, activity__organization__administrators=owner, available__gt=0).exclude(bookings__user=family).first()
        before = slot.available
        booking = services.reserve(family, slot.pk)
        slot.refresh_from_db()
        self.assertEqual(slot.available, before - 1)
        self.assertTrue(access.bookings(owner).filter(pk=booking.pk).exists())
        outside = m.User.objects.get(username='defensa_proveedor_08')
        self.client.force_login(outside)
        self.assertEqual(self.client.get(reverse('document', args=[booking.pk])).status_code, 404)
        services.cancel(family, booking)
        slot.refresh_from_db()
        self.assertEqual(slot.available, before)

    def test_refresh_is_guarded_and_reapplying_migration_is_idempotent(self):
        with self.assertRaises(CommandError):
            call_command('refresh_defense_demo', stdout=StringIO())
        with override_settings(KIDDO_DEFENSE_DEMO=True, KIDDO_ALLOW_DEMO_DATA=True):
            output = StringIO()
            call_command('refresh_defense_demo', stdout=output)
            self.assertIn('0 horarios añadidos', output.getvalue())
            migration = import_module('core.migrations.0013_defense_demo_data')
            migration.load_defense_data(apps, type('Editor', (), {'connection': connection})())
            self.assertEqual(self.bookings.count(), 60)


class DefenseMigrationTests(TransactionTestCase):
    def test_normal_migration_loads_no_defense_accounts_or_operations(self):
        MigrationExecutor(connection).migrate([('core', '0012_provider_publications_demo')])
        with override_settings(KIDDO_DEFENSE_DEMO=False):
            MigrationExecutor(connection).migrate([('core', '0013_defense_demo_data')])
        self.assertFalse(m.DemoScenario.objects.filter(key=seed.KEY).exists())
        self.assertFalse(m.User.objects.filter(username__startswith='defensa_').exists())

    def test_real_migration_adds_fixtures_only_when_opted_in_and_preserves_old_accounts(self):
        target = [('core', '0013_defense_demo_data')]
        executor = MigrationExecutor(connection)
        executor.migrate([('core', '0012_provider_publications_demo')])
        old = executor.loader.project_state([('core', '0012_provider_publications_demo')]).apps
        User = old.get_model('core', 'User')
        existing, _ = User.objects.get_or_create(username='kept-before-defense', defaults={'email': 'kept@example.invalid', 'credits': 13})
        try:
            with override_settings(KIDDO_DEFENSE_DEMO=True, KIDDO_ALLOW_DEMO_DATA=True):
                MigrationExecutor(connection).migrate(target)
            self.assertEqual(m.Booking.objects.filter(schedule__activity__origin_key__startswith=seed.PREFIX).count(), 60)
            self.assertEqual(m.User.objects.get(pk=existing.pk).credits, 13)
        finally:
            MigrationExecutor(connection).migrate(target)
