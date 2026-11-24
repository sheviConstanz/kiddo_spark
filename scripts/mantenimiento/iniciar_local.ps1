$ErrorActionPreference = 'Stop'
. (Join-Path (Split-Path -Parent $PSScriptRoot) 'local-runtime.ps1')

$localUrl = 'http://127.0.0.1:8000/'
$managePath = Join-Path $projectRoot 'manage.py'
$serverArguments = '-B "{0}" runserver 127.0.0.1:8000 --noreload' -f $managePath
$serverPattern = '\s-B\s+"?' + [regex]::Escape($managePath) + '"?\s+runserver\s+127\.0\.0\.1:8000\s+--noreload\s*$'
$previousPythonPath = $env:PYTHONPATH

function Get-ProjectServer($listener) {
    if ($listener.LocalAddress -ne '127.0.0.1') { return }
    $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener.OwningProcess)"
    if ($processInfo.Name -ieq 'python.exe' -and $processInfo.CommandLine -match $serverPattern) {
        return $processInfo
    }
}

Push-Location -LiteralPath $projectRoot
try {
    $listeners = @(Get-LocalListener)
    if ($listeners.Count) {
        if ($listeners.Count -ne 1 -or -not (Get-ProjectServer $listeners[0])) {
            throw 'El puerto 8000 esta ocupado por otro proceso. No se detuvo ninguna aplicacion.'
        }
        Write-Host 'Kiddo Spark esta encendido.'
        if ((Read-Host 'Apagar la demo? [S/N]') -match '^(s|si)$') {
            $current = Get-ProjectServer $listeners[0]
            if (-not $current) { throw 'El proceso cambio. Vuelve a ejecutar el archivo.' }
            Stop-Process -Id $current.ProcessId
            Wait-Process -Id $current.ProcessId -Timeout 5 -ErrorAction SilentlyContinue
            if (@(Get-LocalListener | Where-Object { Get-ProjectServer $_ }).Count) {
                throw 'El proceso de Kiddo Spark sigue encendido.'
            }
            Write-Host 'Kiddo Spark apagado.' -ForegroundColor Green
        } else {
            Write-Host "La demo sigue disponible en $localUrl"
        }
        return
    }

    $pythonPath = Get-LocalPython
    if (-not $pythonPath) { throw 'Ejecuta instalar_local.ps1 antes de encender la demo.' }
    $database = Join-Path $projectRoot 'var\kiddo.sqlite3'
    if (-not (Test-Path -LiteralPath $database -PathType Leaf)) {
        throw 'La base local aun no existe. Ejecuta instalar_local.ps1.'
    }
    Write-Host 'Aplicando actualizaciones de la base local...'
    Invoke-LocalPython manage.py migrate --noinput
    $logs = Join-Path $projectRoot 'var'
    $logOut = Join-Path $logs 'local-server.log'
    $logErr = Join-Path $logs 'local-server-error.log'
    Start-Process -FilePath $pythonPath -ArgumentList $serverArguments -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput $logOut -RedirectStandardError $logErr

    $ready = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        $active = @(Get-LocalListener)
        if ($active.Count -eq 1 -and (Get-ProjectServer $active[0])) {
            $ready = $true
            break
        }
        Start-Sleep -Milliseconds 250
    }
    if (-not $ready) { throw 'No se pudo abrir el servidor local. Revisa var\local-server-error.log.' }
    Write-Host "Kiddo Spark listo: $localUrl" -ForegroundColor Green
    Write-Host 'Para apagarlo, vuelve a ejecutar este archivo y confirma.'
} catch {
    Write-Host ("No se pudo completar la accion. " + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    $env:PYTHONPATH = $previousPythonPath
    Pop-Location
    Read-Host 'Presiona Enter para cerrar' | Out-Null
}
