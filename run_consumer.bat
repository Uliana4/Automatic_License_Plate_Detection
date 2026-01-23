@echo off
REM Skrypt Windows do uruchamiania consumera

echo ======================================================
echo License Plate Recognition - Consumer
echo ======================================================
echo.

echo [1] Instalowanie zależności (jeśli potrzebne)...
pip install -q -r requirements.txt 2>nul
echo.

echo [2] Uruchamianie consumera...
echo Upewnij się, że backend jest uruchomiony w osobnym oknie!
echo.
python -m consumer.plate_analysis_consumer

pause
