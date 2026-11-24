import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import defense_demo


class DefensePreparationTests(unittest.TestCase):
    def test_fresh_selection_keeps_the_previous_database_and_uses_a_new_file(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            previous = folder / 'anterior.sqlite3'
            previous.write_bytes(b'existing demo operations')
            pointer = folder / 'current.json'
            pointer.write_text(json.dumps({'database': previous.name}), encoding='utf-8')
            calls = []

            def run(python, env, *args):
                calls.append((env.copy(), args))
                if args[1] == 'migrate':
                    (folder / env['KIDDO_DEFENSE_DB']).touch(exist_ok=False)

            with patch.object(defense_demo, 'DIRECTORY', folder), patch.object(defense_demo, 'listening', return_value=False), \
                    patch.object(defense_demo, 'prepare_python', side_effect=lambda env: (Path('python.exe'), env)), \
                    patch.object(defense_demo, 'run', side_effect=run), \
                    patch('sys.argv', ['defense_demo.py', '--fresh', '--prepare-only']):
                defense_demo.main()
            selected = json.loads(pointer.read_text())['database']
            self.assertNotEqual(selected, previous.name)
            self.assertEqual(previous.read_bytes(), b'existing demo operations')
            self.assertTrue((folder / selected).exists())
            self.assertEqual(calls[0][0]['DJANGO_SETTINGS_MODULE'], 'kiddo.defense_settings')
            self.assertEqual(calls[1][1], ('manage.py', 'refresh_defense_demo'))

    def test_active_demo_is_not_replaced_during_reinitialization(self):
        with patch('sys.argv', ['defense_demo.py', '--fresh']), patch.object(defense_demo, 'listening', return_value=True), \
                patch.object(defense_demo, 'prepare_python') as prepare:
            with self.assertRaisesRegex(RuntimeError, 'Cierra primero'):
                defense_demo.main()
            prepare.assert_not_called()

    def test_failed_migration_does_not_change_selected_database(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            pointer = folder / 'current.json'
            pointer.write_text('{"database": "conservar.sqlite3"}', encoding='utf-8')
            with patch.object(defense_demo, 'DIRECTORY', folder), patch.object(defense_demo, 'listening', return_value=False), \
                    patch.object(defense_demo, 'prepare_python', side_effect=lambda env: (Path('python.exe'), env)), \
                    patch.object(defense_demo, 'run', side_effect=RuntimeError('migration failed')), \
                    patch('sys.argv', ['defense_demo.py', '--fresh', '--prepare-only']):
                with self.assertRaises(RuntimeError):
                    defense_demo.main()
            self.assertEqual(json.loads(pointer.read_text())['database'], 'conservar.sqlite3')
