@echo off
REM Skrypt Windows do uruchamiania backendu

echo ======================================================
echo License Plate Recognition - Backend API
echo ======================================================
echo.

echo [1] Instalowanie zależności (jeśli potrzebne)...
pip install -q -r requirements.txt 2>nul
echo.

echo [2] Uruchamianie backendu na porcie 8000...
echo.
python -m backend.main

pause
