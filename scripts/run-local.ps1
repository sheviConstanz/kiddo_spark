$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Primero sigue la instalacion del README para crear .venv e instalar requirements.txt.'
}
& $pythonPath manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron preparar las tablas.' }
& $pythonPath manage.py seed_demo
if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar el catalogo.' }
& $pythonPath manage.py runserver 127.0.0.1:8000 --noreload
