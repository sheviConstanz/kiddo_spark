"""Prepare, open or renew the separate defense database without replacing files."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import build_opener, ProxyHandler
import uuid
import webbrowser

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.open_local import ROOT, prepare_python, run


DIRECTORY = ROOT / 'var' / 'defense_data'
URL = 'http://127.0.0.1:8002/'


def listening():
    try:
        with socket.create_connection(('127.0.0.1', 8002), timeout=.5):
            return True
    except OSError:
        return False


def current_server():
    try:
        # The login page sets a defense-only CSRF cookie; the normal demo does not.
        with build_opener(ProxyHandler({})).open(URL + 'ingresar/', timeout=2) as response:
            cookies = ';'.join(response.headers.get_all('Set-Cookie', []))
            return response.status == 200 and 'kiddo_defense_csrf=' in cookies and b'Kiddo Spark' in response.read()
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--fresh', action='store_true', help='Crea otra base de defensa y conserva todos los archivos anteriores.')
    args = parser.parse_args()
    if listening():
        if args.fresh or args.prepare_only:
            raise RuntimeError('Cierra primero la demo de defensa con Ctrl+C. La demo normal puede seguir abierta.')
        if current_server():
            webbrowser.open(URL)
            return
        raise RuntimeError('El puerto 8002 está ocupado. No se detuvo el otro proceso.')
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'kiddo.defense_settings'}
    env.pop('PYTHONPATH', None)
    env.pop('KIDDO_DEFENSE_DB', None)
    if args.fresh:
        name = f'defensa_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}.sqlite3'
    else:
        pointer = DIRECTORY / 'current.json'
        name = json.loads(pointer.read_text(encoding='utf-8'))['database'] if pointer.exists() else 'defensa.sqlite3'
    # Validate the name before handing it to Django or persisting a selection.
    import re
    if not isinstance(name, str) or not re.fullmatch(r'[a-zA-Z0-9_-]+\.sqlite3', name):
        raise RuntimeError('El selector de la base de defensa contiene un nombre inválido.')
    env['KIDDO_DEFENSE_DB'] = name
    runtime = prepare_python(env)
    if runtime is None:
        return
    python, env = runtime
    run(python, env, 'manage.py', 'migrate', '--noinput')
    run(python, env, 'manage.py', 'refresh_defense_demo')
    (DIRECTORY / 'current.json').write_text(json.dumps({'database': name}) + '\n', encoding='utf-8')
    print('Base de defensa lista. Accesos y videos: docs/DEFENSA-DATOS.md', flush=True)
    if args.prepare_only:
        return
    server = subprocess.Popen([str(python), '-B', str(ROOT / 'manage.py'), 'runserver', '127.0.0.1:8002', '--noreload'], cwd=ROOT, env=env)
    try:
        until = time.monotonic() + 20
        while server.poll() is None and time.monotonic() < until:
            if current_server():
                print(f'Demo de defensa lista: {URL} Cierra con Ctrl+C.', flush=True)
                webbrowser.open(URL)
                server.wait()
                return
            time.sleep(.2)
        raise RuntimeError('No se pudo abrir la demo de defensa. Revisa la ventana.')
    except KeyboardInterrupt:
        print('Demo de defensa apagada.')
    finally:
        if server.poll() is None:
            server.terminate()
            server.wait(timeout=10)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f'No se pudo preparar la defensa: {exc}', file=sys.stderr)
        raise SystemExit(1)
