#!/bin/bash
# Skrypt do uruchamiania całego systemu

echo "======================================================"
echo "License Plate Recognition System"
echo "======================================================"
echo ""

# Sprawdzenie zainstalowanych pakietów
echo "[1] Sprawdzanie zainstalowanych pakietów..."
python -m pip list | grep -E "fastapi|opencv|easyocr|redis" || true
echo ""

# Uruchomienie backendu
echo "[2] Uruchamianie backendu na porcie 8000..."
python -m backend.main &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 3
echo ""

# Uruchomienie consumera
echo "[3] Uruchamianie consumera..."
python -m consumer.plate_analysis_consumer &
CONSUMER_PID=$!
echo "Consumer PID: $CONSUMER_PID"
sleep 2
echo ""

echo "======================================================"
echo "System uruchomiony!"
echo "======================================================"
echo ""
echo "Backend API dostępny na: http://localhost:8000"
echo "Dokumentacja Swagger: http://localhost:8000/docs"
echo ""
echo "Aby zatrzymać system, naciśnij Ctrl+C"
echo ""

# Czekanie na przerwanie
wait $BACKEND_PID $CONSUMER_PID
