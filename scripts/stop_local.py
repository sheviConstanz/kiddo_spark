"""Stop the Windows demo associated with this checkout."""

import ctypes
from ctypes import wintypes
import os
import subprocess
import sys

from scripts.open_local import HOST, PORT, ROOT, VENV_PYTHON, is_listening


FIND_SERVER = r"""
$ErrorActionPreference = 'Stop'
$listeners = @(Get-NetTCPConnection -State Listen | Where-Object LocalPort -eq $env:KIDDO_STOP_PORT)
if ($listeners.Count -eq 0) { return }
if ($listeners.Count -eq 1 -and $listeners[0].LocalAddress -eq $env:KIDDO_STOP_HOST) {
    $server = Get-CimInstance Win32_Process -Filter "ProcessId = $($listeners[0].OwningProcess)"
    $manage = [regex]::Escape($env:KIDDO_STOP_MANAGE)
    $bind = [regex]::Escape($env:KIDDO_STOP_HOST + ':' + $env:KIDDO_STOP_PORT)
    $suffix = '\s+runserver\s+' + $bind + '\s+--noreload\s*$'
    if ($server.Name -ieq 'python.exe' -and (
        $server.CommandLine -match ('\s(?:"' + $manage + '"|' + $manage + ')' + $suffix) -or
        ($server.ExecutablePath -ieq $env:KIDDO_STOP_VENV -and
            $server.CommandLine -match ('\s"?manage\.py"?' + $suffix))
    )) {
        $server.ProcessId
        return
    }
}
'foreign'
"""


def server_pid():
    env = {
        **os.environ,
        'KIDDO_STOP_HOST': HOST,
        'KIDDO_STOP_PORT': str(PORT),
        'KIDDO_STOP_MANAGE': str(ROOT / 'manage.py'),
        'KIDDO_STOP_VENV': str(VENV_PYTHON),
    }
    result = subprocess.run(
        ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', FIND_SERVER],
        env=env, capture_output=True, text=True, check=True, timeout=15,
    ).stdout.strip()
    if not result:
        return None
    if not result.isascii() or not result.isdecimal():
        raise RuntimeError(f'El puerto {PORT} pertenece a otro proceso. Se dejó ejecutando.')
    return int(result)


def stop_server(pid):
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    process_terminate = 0x0001
    synchronize = 0x00100000
    handle = kernel.OpenProcess(process_terminate | synchronize, False, pid)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        if server_pid() != pid:
            raise RuntimeError('El proceso cambió. Vuelve a abrir este archivo.')
        # Exit successfully so the original launcher closes after the server stops.
        if not kernel.TerminateProcess(handle, 0):
            raise ctypes.WinError(ctypes.get_last_error())
        if kernel.WaitForSingleObject(handle, 5000) != 0:
            raise RuntimeError('No se pudo confirmar el cierre del servidor.')
    finally:
        kernel.CloseHandle(handle)


def main():
    pid = server_pid()
    if pid is None:
        print('Kiddo Spark ya está apagado.')
        return
    stop_server(pid)
    if is_listening():
        raise RuntimeError(f'El puerto {PORT} todavía está ocupado. Revisa si se abrió otra instancia.')
    print('Kiddo Spark apagado.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f'No se pudo apagar Kiddo Spark. {exc}', file=sys.stderr)
        sys.exit(1)
