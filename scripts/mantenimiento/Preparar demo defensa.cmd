@echo off
setlocal
title Kiddo Spark - Preparar datos de defensa
pushd "%~dp0..\.." || exit /b 1
python.exe -E -B scripts\defense_demo.py --prepare-only
set "kiddo_result=%errorlevel%"
pause
popd
exit /b %kiddo_result%
