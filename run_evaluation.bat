@echo off
REM Skrypt Windows do uruchamiania ewaluacji

echo ======================================================
echo License Plate Recognition - Algorithm Evaluation
echo ======================================================
echo.

echo [1] Instalowanie zależności (jeśli potrzebne)...
pip install -q -r requirements.txt 2>nul
echo.

echo [2] Uruchamianie ewaluacji algorytmu...
python -m tests.evaluate_algorithm

pause
