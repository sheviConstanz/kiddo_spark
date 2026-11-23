"""Explicit local demo fixture loading, without starting a service."""
import os
from subprocess import CalledProcessError

from open_local import ROOT, prepare_python, run


def main():
    env = {**os.environ, 'DJANGO_SETTINGS_MODULE': 'kiddo.settings'}
    env.pop('PYTHONPATH', None)
    runtime = prepare_python(env)
    if runtime is None:
        return
    python, env = runtime
    (ROOT / 'var').mkdir(exist_ok=True)
    run(python, env, 'manage.py', 'migrate', '--noinput')
    run(python, env, 'manage.py', 'seed_demo')
    run(python, env, 'manage.py', 'seed_demo', '--scenario')
    print('Listo. Abre Kiddo Spark y consulta docs/DEMO-ACADEMICA.md. Los datos anteriores se conservaron.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, CalledProcessError) as exc:
        print(f'No se pudo preparar la demostración: {exc}')
        raise SystemExit(1)
