@echo off
setlocal
title Kiddo Spark - Datos de demostracion
pushd "%~dp0..\.." || exit /b 1
where python.exe >nul 2>&1
if errorlevel 1 (
    echo No se encontro Python. Revisa el README.
    pause
    popd
    exit /b 1
)
python.exe -E -B scripts\load_demo.py
set "kiddo_result=%errorlevel%"
pause
popd
exit /b %kiddo_result%
