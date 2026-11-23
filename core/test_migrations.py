from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone


class PublicationMigrationTests(TransactionTestCase):
    def test_upgrade_preserves_existing_activity_booking_and_balance(self):
        old_target = [('core', '0011_provider_booking_notice')]
        new_target = [('core', '0012_provider_publications_demo')]
        executor = MigrationExecutor(connection)
        executor.migrate(old_target)
        try:
            old = executor.loader.project_state(old_target).apps
            user = old.get_model('core', 'User').objects.create(username='historical-migration', email='migration@example.invalid', credits=17, points=50)
            city = old.get_model('core', 'City').objects.create(name='Comuna histórica de prueba')
            category = old.get_model('core', 'Category').objects.create(name='Categoría histórica de prueba')
            center = old.get_model('core', 'Organization').objects.create(name='Centro histórico', city=city, email='center@example.invalid', created_by=user, approved=True)
            Activity = old.get_model('core', 'Activity')
            live = Activity.objects.create(name='Publicada anterior', category=category, organization=center, description='Conservar', active=True)
            paused = Activity.objects.create(name='Inactiva anterior', category=category, organization=center, active=False)
            slot = old.get_model('core', 'Schedule').objects.create(activity=live, starts_at=timezone.now(), capacity=10, available=9)
            booking = old.get_model('core', 'Booking').objects.create(user=user, schedule=slot, sparks=4, amount=23000)
            executor = MigrationExecutor(connection)
            executor.migrate(new_target)
            current = executor.loader.project_state(new_target).apps
            self.assertEqual(current.get_model('core', 'Activity').objects.get(pk=live.pk).publication_status, 'published')
            self.assertEqual(current.get_model('core', 'Activity').objects.get(pk=paused.pk).publication_status, 'paused')
            saved = current.get_model('core', 'User').objects.get(pk=user.pk)
            self.assertEqual((saved.credits, saved.points), (17, 50))
            self.assertEqual(current.get_model('core', 'Booking').objects.get(pk=booking.pk).amount, 23000)
            self.assertEqual(current.get_model('core', 'Schedule').objects.get(pk=slot.pk).available, 9)
        finally:
            MigrationExecutor(connection).migrate(new_target)
