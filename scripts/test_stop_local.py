from pathlib import Path
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import open_local, stop_local


class LocalShutdownTests(unittest.TestCase):
    def test_already_stopped_needs_no_termination(self):
        with patch.object(stop_local, 'server_pid', return_value=None), patch.object(stop_local, 'stop_server') as stop:
            stop_local.main()
        stop.assert_not_called()

    @unittest.skipUnless(sys.platform == 'win32', 'Uses a Windows listener and process handles')
    def test_stops_only_the_matching_checkout_and_releases_its_port(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            manage = root / 'manage.py'
            manage.write_text(
                'import socket, sys, time\n'
                'with socket.socket() as listener:\n'
                '    listener.bind(("127.0.0.1", int(sys.argv[2].split(":")[1])))\n'
                '    listener.listen()\n'
                '    print(listener.getsockname()[1], flush=True)\n'
                '    time.sleep(30)\n',
                encoding='utf-8',
            )
            launcher = (
                'import subprocess, sys; '
                'server = subprocess.Popen(sys.argv[1:], stdout=subprocess.PIPE, text=True); '
                'print(server.stdout.readline().strip(), flush=True); '
                'raise SystemExit(server.wait())'
            )
            with socket.socket() as candidate:
                candidate.bind(('127.0.0.1', 0))
                port = candidate.getsockname()[1]
            with subprocess.Popen(
                [sys.executable, '-B', '-c', launcher, sys.executable, '-B', str(manage),
                 'runserver', f'127.0.0.1:{port}', '--noreload'],
                stdout=subprocess.PIPE, text=True,
            ) as process:
                self.assertEqual(process.stdout.readline().strip(), str(port))
                with patch.object(stop_local, 'PORT', port), patch.object(open_local, 'PORT', port):
                    with self.assertRaisesRegex(RuntimeError, 'otro proceso'):
                        stop_local.main()
                    self.assertTrue(open_local.is_listening())
                    with patch.object(stop_local, 'ROOT', root):
                        stop_local.main()
                        self.assertIsNone(stop_local.server_pid())
                    self.assertFalse(open_local.is_listening())
                self.assertEqual(process.wait(timeout=5), 0)
