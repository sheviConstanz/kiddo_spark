$ErrorActionPreference = 'Stop'
. (Join-Path (Split-Path -Parent $PSScriptRoot) 'local-runtime.ps1')

$previousPythonPath = $env:PYTHONPATH
$previousOrigin = $env:KIDDO_TUNNEL_ORIGIN
$tunnelProcess = $null
$djangoProcess = $null
$djangoWorker = $null
$failed = $false

Push-Location -LiteralPath $projectRoot
try {
    $tunnelCli = Get-Command devtunnel.exe -CommandType Application -ErrorAction SilentlyContinue
    if (-not $tunnelCli) { throw 'Instala Microsoft Dev Tunnels CLI y sigue el apartado de demo remota del README.' }
    $pythonPath = Get-LocalPython
    if (-not $pythonPath) { throw 'Ejecuta instalar_local.ps1 antes de compartir la demo.' }
    if (@(Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue).Count) {
        throw 'El puerto 8001 esta ocupado. No se detuvo ninguna aplicacion.'
    }
    if ((Read-Host 'Abrir un tunel privado por Internet para la demo aislada? [S/N]') -notmatch '^(s|si)$') {
        return
    }

    $logs = Join-Path $projectRoot 'var'
    $tunnelLog = Join-Path $logs 'kiddo-tunnel.log'
    $tunnelErrorLog = Join-Path $logs 'kiddo-tunnel-error.log'
    $tunnelProcess = Start-Process -FilePath $tunnelCli.Source -ArgumentList 'host','-p','8001','--protocol','http','--expiration','1h' -WindowStyle Hidden -RedirectStandardOutput $tunnelLog -RedirectStandardError $tunnelErrorLog -PassThru
    $hostLinePattern = '(?m)^\s*Hosting port 8001 at .*?(https://[a-z0-9-]+-8001(?:\.[a-z0-9-]+)?\.devtunnels\.ms)/'
    $remoteOrigin = $null
    for ($attempt = 0; $attempt -lt 80; $attempt++) {
        if ($tunnelProcess.HasExited) { break }
        foreach ($log in $tunnelLog, $tunnelErrorLog) {
            $output = Get-Content -LiteralPath $log -Raw -ErrorAction SilentlyContinue
            if ($output -match $hostLinePattern) {
                $remoteOrigin = $Matches[1]
                break
            }
        }
        if ($remoteOrigin) { break }
        Start-Sleep -Milliseconds 500
    }
    if (-not $remoteOrigin) {
        throw 'No se obtuvo la direccion del tunel. Comprueba devtunnel user login y los registros en var.'
    }

    $env:KIDDO_TUNNEL_ORIGIN = $remoteOrigin
    Invoke-LocalPython manage.py migrate --noinput --settings=kiddo.tunnel_settings
    Invoke-LocalPython manage.py seed_demo --settings=kiddo.tunnel_settings
    $managePath = Join-Path $projectRoot 'manage.py'
    $serverArguments = '-B "{0}" runserver 127.0.0.1:8001 --noreload --settings=kiddo.tunnel_settings' -f $managePath
    $djangoProcess = Start-Process -FilePath $pythonPath -ArgumentList $serverArguments -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'kiddo-tunnel-django.log') -RedirectStandardError (Join-Path $logs 'kiddo-tunnel-django-error.log') -PassThru

    $ready = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        if ($djangoProcess.HasExited -or $tunnelProcess.HasExited) { break }
        $listener = @(Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue)
        if ($listener.Count -eq 1 -and $listener[0].LocalAddress -eq '127.0.0.1') {
            $listenerProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener[0].OwningProcess)"
            if ($listenerProcess.ProcessId -eq $djangoProcess.Id -or $listenerProcess.ParentProcessId -eq $djangoProcess.Id) {
                if ($listenerProcess.ProcessId -ne $djangoProcess.Id) {
                    $djangoWorker = Get-Process -Id $listenerProcess.ProcessId
                }
                $ready = $true
                break
            }
        }
        Start-Sleep -Milliseconds 250
    }
    if (-not $ready) { throw 'No se pudo iniciar la copia de la demo. Revisa los registros en var.' }
    Write-Host "Enlace privado: $remoteOrigin/" -ForegroundColor Green
    Write-Host 'Entra con la misma cuenta que utilizaste en devtunnel user login.'
    Read-Host 'Presiona Enter para cerrar la demo remota y el tunel' | Out-Null
} catch {
    Write-Host ("No se pudo compartir Kiddo Spark. " + $_.Exception.Message) -ForegroundColor Red
    $failed = $true
} finally {
    foreach ($process in $tunnelProcess, $djangoWorker, $djangoProcess) {
        try {
            if ($process -and -not $process.HasExited) { $process.Kill() }
        } catch {
            Write-Warning "No se pudo cerrar un proceso de esta sesion: $($_.Exception.Message)"
        }
    }
    $env:PYTHONPATH = $previousPythonPath
    $env:KIDDO_TUNNEL_ORIGIN = $previousOrigin
    Pop-Location
}
if ($failed) {
    Read-Host 'Presiona Enter para cerrar' | Out-Null
    exit 1
}
