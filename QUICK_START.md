# Quick Start Guide

## Szybki start w 5 minut

### 1. Instalacja zależności

```bash
pip install -r requirements.txt
```

**Uwaga**: Pierwsza instalacja EasyOCR pobierze model (~100MB) - może chwilę potrwać.

### 2. Quick Test (test pierwszych 5 zdjęć)

Aby szybko sprawdzić czy wszystko działa:

```bash
# Windows
python quick_test.py

# Linux/Mac
python3 quick_test.py
```

Zobaczysz wyniki dla pierwszych 5 zdjęć z datasetu.

### 3. Pełna ewaluacja

Aby ocenić algorytm na całym zbiorze:

```bash
# Windows
python -m tests.evaluate_algorithm

# Linux/Mac
python3 -m tests.evaluate_algorithm
```

### 4. Uruchamianie API

Terminal 1 - Backend:
```bash
# Windows
python -m backend.main

# Linux/Mac
python3 -m backend.main
```

Dostępny będzie na: `http://localhost:8000`
Dokumentacja: `http://localhost:8000/docs`

Terminal 2 - Consumer:
```bash
# Windows
python -m consumer.plate_analysis_consumer

# Linux/Mac
python3 -m consumer.plate_analysis_consumer
```

Terminal 3 - Testy API:
```bash
# Windows
python -m tests.test_api

# Linux/Mac
python3 -m tests.test_api
```

## Testowanie endpoints

### Bezpośrednia analiza
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@photos/1.jpg"
```

### Dodanie do kolejki
```bash
curl -X POST "http://localhost:8000/queue-analysis" \
  -F "file=@photos/2.jpg"
```

### Status kolejki
```bash
curl "http://localhost:8000/queue-status"
```

## Wymagania sprzętowe

- CPU: 2+ rdzenie
- RAM: 4GB minimum (8GB+ zalecane dla EasyOCR)
- Dysk: 2GB wolnego miejsca (dla modeli)

## Czasy oczekiwania

- Pierwsza uruchomienie (pobieranie modelu): ~2-3 minuty
- Każde zdjęcie: ~0.2-0.5 sekundy (zależy od rozmiaru i CPU)

## Rozwiązywanie problemów

### Błąd: "No module named 'easyocr'"

```bash
pip install easyocr
```

### Błąd: "Connection refused" dla Redis

```bash
# Instalacja Redis (na Windows, użyj WSL lub Docker)
docker run -d -p 6379:6379 redis:latest
```

Lub zmień `.env`:
```
QUEUE_SYSTEM=sqlite  # Alternatywa bez Redis
```

### Długi czas pierwszego przetwarzania

To normalne - EasyOCR pobiera model za pierwszym razem (~100MB).
Kolejne zdjęcia będą szybsze.

## Struktura danych wyjściowych

Po uruchomieniu ewaluacji otrzymasz raport:

```
============================================================
RAPORT EWALUACJI ALGORYTMU DETEKCJI TABLIC
============================================================
Całkowita liczba zdjęć: 59
Poprawnie odczytane tablice: 50
Dokładność (Accuracy): 84.75%
Średnia miara IoU: 0.8234
Całkowity czas przetwarzania: 12.34s
Średni czas na zdjęcie: 0.2090s

OCENA KOŃCOWA: 4.5
============================================================
```

## Dalsze kroki

1. ✓ Uruchomi się ewaluacja
2. ✓ Zobaczysz wynik OCR
3. ✓ Otrzymasz ocenę końcową (2.0-5.0)
4. ✓ Wyniki będą zapisane w bazie SQLite (`database.db`)

Powodzenia! 🚗
