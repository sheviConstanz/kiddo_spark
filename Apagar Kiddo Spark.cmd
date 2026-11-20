@echo off
setlocal
title Apagar Kiddo Spark
pushd "%~dp0" || exit /b 1
where python.exe >nul 2>&1
if errorlevel 1 (
    echo No se encontro Python. Revisa la seccion "Antes de empezar en Windows" del README.
    pause
    popd
    exit /b 1
)
python.exe -E -B -m scripts.stop_local
set "kiddo_result=%errorlevel%"
pause
popd
exit /b %kiddo_result%
