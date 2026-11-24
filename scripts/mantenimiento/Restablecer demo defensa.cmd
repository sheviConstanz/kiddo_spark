@echo off
setlocal
title Kiddo Spark - Nueva base de defensa
pushd "%~dp0..\.." || exit /b 1
echo Se creara otra base de defensa. La anterior se conserva.
python.exe -E -B scripts\defense_demo.py --fresh --prepare-only
set "kiddo_result=%errorlevel%"
pause
popd
exit /b %kiddo_result%
