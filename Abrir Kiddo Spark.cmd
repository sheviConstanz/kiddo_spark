@echo off
setlocal
title Kiddo Spark
pushd "%~dp0" || exit /b 1
where python.exe >nul 2>&1
if errorlevel 1 (
    echo No se encontro Python. Revisa la seccion "Antes de empezar en Windows" del README.
    pause
    popd
    exit /b 1
)
python.exe -E -B scripts\open_local.py
set "kiddo_result=%errorlevel%"
if not "%kiddo_result%"=="0" pause
popd
exit /b %kiddo_result%
