from pathlib import Path
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import open_local


class LocalLauncherTests(unittest.TestCase):
    def test_second_click_reuses_the_open_demo(self):
        with patch.object(open_local, 'is_listening', return_value=True), \
                patch.object(open_local, 'is_kiddo_spark', return_value=True), \
                patch.object(open_local.webbrowser, 'open') as open_page, \
                patch.object(open_local, 'prepare_python') as prepare:
            open_local.main()
        prepare.assert_not_called()
        open_page.assert_called_once_with('http://127.0.0.1:8000/')

    def test_conflicting_server_is_left_alone(self):
        with patch.object(open_local, 'is_listening', return_value=True), \
                patch.object(open_local, 'is_kiddo_spark', return_value=False), \
                patch.object(open_local.webbrowser, 'open') as open_page:
            with self.assertRaisesRegex(RuntimeError, 'puerto 8000'):
                open_local.main()
        open_page.assert_not_called()

    def test_declining_download_does_not_run_installer(self):
        with TemporaryDirectory() as temporary, \
                patch.object(open_local, 'VENV', Path(temporary)), \
                patch.object(open_local, 'has_dependencies', return_value=False), \
                patch('builtins.input', return_value='N'), \
                patch.object(open_local, 'run') as run:
            self.assertIsNone(open_local.prepare_python({}))
        run.assert_not_called()

    def test_seed_retries_after_failure_and_does_not_replace_existing_data(self):
        with TemporaryDirectory() as temporary, patch.object(open_local, 'ROOT', Path(temporary)):
            database = Path(temporary) / 'var' / 'kiddo.sqlite3'
            calls = []

            def run_step(python, env, *args):
                calls.append(args[1])
                if args[1] == 'migrate':
                    database.touch(exist_ok=True)
                elif calls.count('seed_demo') == 1:
                    raise CalledProcessError(1, args)

            with patch.object(open_local, 'run', side_effect=run_step):
                with self.assertRaises(CalledProcessError):
                    open_local.prepare_database(Path('python.exe'), {})
                open_local.prepare_database(Path('python.exe'), {})
                open_local.prepare_database(Path('python.exe'), {})
            self.assertEqual(calls, ['migrate', 'seed_demo', 'migrate', 'seed_demo', 'migrate'])
