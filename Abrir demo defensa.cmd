@echo off
setlocal
title Kiddo Spark - Defensa academica
pushd "%~dp0" || exit /b 1
python.exe -E -B scripts\defense_demo.py
set "kiddo_result=%errorlevel%"
if not "%kiddo_result%"=="0" pause
popd
exit /b %kiddo_result%
