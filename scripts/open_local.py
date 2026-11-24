"""Prepare and open the local academic demo without PowerShell."""

import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener
import webbrowser


ROOT = Path(__file__).resolve().parents[1]
PORT = 8000
HOST = '127.0.0.1'
VENV = ROOT / '.venv'
VENV_PYTHON = VENV / 'Scripts' / 'python.exe'
SUPPORTED_PYTHON = ((3, 14), (3, 15))
CHECK_REQUIREMENTS = """
import sys
from importlib.metadata import version
from pathlib import Path
import django
pins = [line.strip().split('==', 1) for line in Path('requirements.txt').read_text().splitlines()
        if line.strip() and not line.lstrip().startswith('#')]
raise SystemExit(sys.version_info[:2] not in ((3, 14), (3, 15))
                 or not all(version(name) == expected for name, expected in pins))
"""


def command(python, *args):
    return [str(python), '-B', *map(str, args)]


def run(python, env, *args):
    subprocess.run(command(python, *args), cwd=ROOT, env=env, check=True)


def has_dependencies(python, env):
    if not python.is_file():
        return False
    return subprocess.run(
        command(python, '-c', CHECK_REQUIREMENTS), cwd=ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def prepare_python(env):
    if has_dependencies(VENV_PYTHON, env):
        return VENV_PYTHON, env

    system_python = Path(sys.executable)
    cached_packages = VENV / 'Lib' / 'site-packages'
    if cached_packages.is_dir():
        cached_env = {**env, 'PYTHONPATH': str(cached_packages)}
        if has_dependencies(system_python, cached_env):
            return system_python, cached_env

    if sys.version_info[:2] not in SUPPORTED_PYTHON:
        raise RuntimeError('Instala Python 3.14 o 3.15. Los pasos están en el README.')
    if input('Preparar la demo y descargar lo que falta? [S/N] ').strip().casefold() not in {'s', 'sí', 'si'}:
        return None
    run(system_python, env, '-m', 'venv', VENV)
    run(VENV_PYTHON, env, '-m', 'pip', 'install', '--no-deps', '-r', 'requirements.txt')
    if not has_dependencies(VENV_PYTHON, env):
        raise RuntimeError('La instalación quedó incompleta. Revisa los mensajes de esta ventana.')
    return VENV_PYTHON, env


def prepare_database(python, env):
    data = ROOT / 'var'
    data.mkdir(exist_ok=True)
    pending = data / '.opening-seed-pending'
    if not (data / 'kiddo.sqlite3').is_file():
        pending.touch(exist_ok=True)
    run(python, env, 'manage.py', 'migrate', '--noinput')
    if pending.is_file():
        run(python, env, 'manage.py', 'seed_demo')
        pending.unlink(missing_ok=True)


def is_listening():
    try:
        with socket.create_connection((HOST, PORT), timeout=0.5):
            return True
    except OSError:
        return False


def is_kiddo_spark(url):
    # Restrict this check to the local port, including when HTTP redirects.
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    try:
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(url, timeout=1) as response:
            return response.status == 200 and b'<title>Kiddo Spark' in response.read(8192)
    except (OSError, URLError):
        return False


def serve(python, env, url):
    process = subprocess.Popen(
        command(python, ROOT / 'manage.py', 'runserver', f'{HOST}:{PORT}', '--noreload'), cwd=ROOT, env=env,
    )
    try:
        deadline = time.monotonic() + 25
        while process.poll() is None and time.monotonic() < deadline:
            if is_kiddo_spark(url):
                if process.poll() is not None:
                    break
                print(f'Demo lista: {url}\nPara apagar, pulsa Ctrl+C o abre Apagar Kiddo Spark en scripts/mantenimiento.', flush=True)
                webbrowser.open(url)
                if process.wait():
                    raise RuntimeError('La demo se cerró con un error.')
                return
            time.sleep(0.25)
        raise RuntimeError(f'La demo no pudo abrirse en {url}. Lee el mensaje anterior.')
    except KeyboardInterrupt:
        print('\nDemo apagada.')
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait()


def main():
    url = f'http://{HOST}:{PORT}/'
    if is_listening():
        if is_kiddo_spark(url):
            print(f'Kiddo Spark ya está abierto: {url}')
            webbrowser.open(url)
            return
        raise RuntimeError('Otra aplicación usa el puerto 8000. Ciérrala antes de abrir la demo.')

    env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'kiddo.settings', 'DJANGO_DEBUG': '0'}
    for name in ('PYTHONPATH', 'DJANGO_ALLOWED_HOSTS', 'DJANGO_CSRF_TRUSTED_ORIGINS'):
        env.pop(name, None)
    runtime = prepare_python(env)
    if runtime is None:
        print('Preparación cancelada.')
        return
    python, env = runtime
    prepare_database(python, env)
    serve(python, env, url)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nOperación cancelada.')
    except (EOFError, OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f'No se pudo abrir Kiddo Spark. {exc}', file=sys.stderr)
        sys.exit(1)
