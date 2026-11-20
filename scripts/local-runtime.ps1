$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot '.venv'
$venvPython = Join-Path $venvPath 'Scripts\python.exe'
$cachedPackages = Join-Path $venvPath 'Lib\site-packages'

function Get-SystemPython {
    Get-Command python.exe -CommandType Application -ErrorAction SilentlyContinue |
        Where-Object { $_.Source -notlike '*\WindowsApps\python.exe' } |
        Select-Object -First 1 -ExpandProperty Source
}

function Test-LocalDependencies($interpreter) {
    $check = @'
import django
from importlib.metadata import version
from pathlib import Path

pins = [
    line.strip().split('==', 1)
    for line in Path('requirements.txt').read_text().splitlines()
    if line.strip() and not line.lstrip().startswith('#')
]
raise SystemExit(not all(version(name) == value for name, value in pins))
'@
    try {
        $check | & $interpreter -B - 2>$null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Get-LocalPython {
    $env:PYTHONPATH = $null
    if ((Test-Path -LiteralPath $venvPython -PathType Leaf) -and (Test-LocalDependencies $venvPython)) {
        return $venvPython
    }
    $systemPython = Get-SystemPython
    if ($systemPython -and (Test-Path -LiteralPath $cachedPackages -PathType Container)) {
        $env:PYTHONPATH = $cachedPackages
        if (Test-LocalDependencies $systemPython) { return $systemPython }
    }
    $env:PYTHONPATH = $null
}

function Invoke-LocalPython {
    & $pythonPath -B @args
    if ($LASTEXITCODE -ne 0) {
        throw "El paso anterior fallo (codigo $LASTEXITCODE)."
    }
}

function Get-LocalListener {
    Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
}
