import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
MAINTENANCE = Path('scripts/mantenimiento')


@unittest.skipUnless(sys.platform == 'win32', 'Windows batch files')
class WindowsLauncherTests(unittest.TestCase):
    def test_launchers_resolve_project_from_another_working_directory(self):
        launchers = {
            Path('Abrir demo defensa.cmd'): ('defense_demo.py', []),
            MAINTENANCE / 'Abrir Kiddo Spark.cmd': ('open_local.py', []),
            MAINTENANCE / 'Apagar Kiddo Spark.cmd': ('stop_local.py', []),
            MAINTENANCE / 'Cargar datos demo.cmd': ('load_demo.py', []),
            MAINTENANCE / 'Preparar demo defensa.cmd': ('defense_demo.py', ['--prepare-only']),
            MAINTENANCE / 'Restablecer demo defensa.cmd': ('defense_demo.py', ['--fresh', '--prepare-only']),
        }
        child_env = dict(os.environ, PATH=str(Path(sys.executable).parent) + os.pathsep + os.environ['PATH'])
        with TemporaryDirectory() as staging:
            root = Path(staging) / 'Kiddo Spark test'
            (root / MAINTENANCE).mkdir(parents=True)
            (root / 'scripts/__init__.py').touch()
            for launcher, (script, args) in launchers.items():
                with self.subTest(launcher=launcher):
                    shutil.copyfile(ROOT / launcher, root / launcher)
                    (root / 'scripts' / script).write_text(
                        'import json, os, sys\n'
                        "print(json.dumps({'cwd': os.getcwd(), 'script': __file__, 'args': sys.argv[1:]}))\n",
                        encoding='utf-8',
                    )
                    result = subprocess.run(
                        [os.environ['COMSPEC'], '/d', '/c', 'call', str(root / launcher)],
                        cwd=staging, env=child_env, input='\n', text=True,
                        capture_output=True, timeout=10,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    data = next(json.loads(line) for line in result.stdout.splitlines() if line.startswith('{'))
                    self.assertEqual(Path(data['cwd']).resolve(), root.resolve())
                    self.assertEqual(Path(data['script']).resolve(), root.resolve() / 'scripts' / script)
                    self.assertEqual(data['args'], args)
