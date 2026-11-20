$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'scripts\local-runtime.ps1')

$previousPythonPath = $env:PYTHONPATH
Push-Location -LiteralPath $projectRoot
try {
    if (@(Get-LocalListener).Count) {
        throw 'El puerto 8000 esta en uso. Apaga la demo antes de instalar o actualizar.'
    }
    $pythonPath = Get-LocalPython
    if (-not $pythonPath) {
        $pythonPath = Get-SystemPython
        if (-not $pythonPath) {
            throw 'Instala Python 3.14 o 3.15 para Windows y vuelve a ejecutar este archivo.'
        }
        if ((Read-Host 'Se necesitan descargar dependencias. Continuar? [S/N]') -notmatch '^(s|si)$') {
            Write-Host 'Instalacion cancelada.'
            return
        }
        Invoke-LocalPython -m venv $venvPath
        $pythonPath = $venvPython
        Invoke-LocalPython -m pip install --no-deps -r requirements.txt
        if (-not (Test-LocalDependencies $pythonPath)) {
            throw 'Las dependencias instaladas no coinciden con requirements.txt.'
        }
    }

    Write-Host 'Preparando la base y el catalogo de demostracion...'
    Invoke-LocalPython manage.py migrate --noinput
    Invoke-LocalPython manage.py seed_demo
    $adminCheck = @'
import os

import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kiddo.settings')
django.setup()
print(int(get_user_model().objects.filter(is_superuser=True, is_active=True).exists()))
'@
    $adminExists = $adminCheck | & $pythonPath -B -
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo comprobar la cuenta de superadministracion.' }
    if ($adminExists -eq '0' -and (Read-Host 'Crear una cuenta de superadministracion para la demo? [S/N]') -match '^(s|si)$') {
        Invoke-LocalPython manage.py createsuperuser
    }
    Write-Host 'Instalacion lista. Ejecuta iniciar_local.ps1 para encender la demo.' -ForegroundColor Green
} catch {
    Write-Host ("No se pudo completar la instalacion. " + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    $env:PYTHONPATH = $previousPythonPath
    Pop-Location
    Read-Host 'Presiona Enter para cerrar' | Out-Null
}
