# Instrukcja dla egzaminatora

## Szybka ocena projektu (10 minut)

### 1. Sprawdzenie brancha
```bash
git branch -a
# Powinien być: automatic_plate_number_recognition
git log --oneline
# Powinny być commity z opisami
```

### 2. Szybki test (5 minut)
```bash
pip install -r requirements.txt
python quick_test.py
```

**Oczekiwany wynik**: 
- Ewaluacja na 5 zdjęciach
- Wyświetlona ocena końcowa (2.0-5.0)

### 3. Pełna ewaluacja (30 sekund na 60 zdjęciach)
```bash
python -m tests.evaluate_algorithm
```

**Oczekiwany raport**:
```
============================================================
RAPORT EWALUACJI ALGORYTMU DETEKCJI TABLIC
============================================================
Całkowita liczba zdjęć: 59
Poprawnie odczytane tablice: [X]
Dokładność (Accuracy): [XX]%
Średnia miara IoU: 0.[XXXX]
Całkowity czas przetwarzania: [XX]s
Średni czas na zdjęcie: 0.[XXXX]s

OCENA KOŃCOWA: [X.X]
============================================================
```

---

## Demonstracja funkcjonalności (15 minut)

### Terminal 1 - Backend API
```bash
python -m backend.main
# Dostępny: http://localhost:8000/docs (Swagger UI)
```

### Terminal 2 - Consumer (asynchroniczny)
```bash
python -m consumer.plate_analysis_consumer
```

### Terminal 3 - Testowanie API
```bash
# Bezpośrednia analiza
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@photos/1.jpg"

# Dodanie do kolejki
curl -X POST "http://localhost:8000/queue-analysis" \
  -F "file=@photos/2.jpg"

# Status kolejki
curl "http://localhost:8000/queue-status"
```

---

## Extended Scope - Kamera (opcjonalnie)

### Uruchomienie monitora z kamerą
```bash
python run_camera_monitor.py
```

**Funkcjonalność**:
- Przechwytuje ramki z kamery
- Real-time detekcja tablic
- Wyświetla wyniki na ekranie
- Zapisuje do bazy danych

---

## Struktura kodu

### Główne komponenty

1. **Backend** (`backend/main.py`)
   - FastAPI serwer
   - 2 endpoints: `/analyze`, `/queue-analysis`
   - Queue management
   - Database storage

2. **Consumer** (`consumer/plate_analysis_consumer.py`)
   - Asynchroniczne przetwarzanie
   - Czyta z kolejki
   - Zapisuje wyniki

3. **Plate Detector** (`utils/plate_detector.py`)
   - EasyOCR
   - Detekcja + OCR
   - Filtrowanie wyników

4. **Evaluation** (`utils/evaluation.py`)
   - Metryki: accuracy, IoU, czas
   - Ocena końcowa 2.0-5.0

5. **Database** (`backend/database.py`)
   - SQLite
   - Przechowywanie wyników

6. **Camera Monitor** (`utils/camera_monitor.py`)
   - Extended scope
   - Real-time monitoring

---

## Dokumentacja dostępna

- `README.md` - Ogólny opis
- `QUICK_START.md` - Szybki start
- `TECHNICAL.md` - Dokumentacja techniczna
- `CHECKLIST.md` - Pełna lista wymagań ✓

---

## Kluczowe wymagania spełnione

✓ **Detekcja tablicy** - EasyOCR
✓ **OCR** - Odczyt znaków
✓ **Dokładność** - Accuracy metryka
✓ **Czas przetwarzania** - Zliczony dla 100 zdjęć
✓ **IoU** - Intersection over Union
✓ **Ocena końcowa** - Formula 2.0-5.0
✓ **API endpoints** - 2 warianty analizy
✓ **Queue system** - Redis/RabbitMQ
✓ **Consumer** - Asynchroniczny
✓ **Database** - SQLite
✓ **Test 30%** - Dla oceny IoU
✓ **Extended scope** - Monitor z kamerą
✓ **Git branch** - automatic_plate_number_recognition
✓ **Dokumentacja** - Kompletna

---

## Scenariusze testowania

### Scenariusz 1: Szybka ocena (5 min)
```
1. git branch -a              # Sprawdzenie brancha
2. python quick_test.py       # Test na 5 zdjęciach
3. Sprawdzenie wyniku         # Czy ocena 2.0-5.0?
```

### Scenariusz 2: Pełna ewaluacja (1 min)
```
1. python -m tests.evaluate_algorithm
2. Sprawdzenie metryki        # Accuracy, IoU, czas
3. Sprawdzenie oceny          # Czy w zakresie 2.0-5.0?
```

### Scenariusz 3: Demonstracja API (5 min)
```
1. Terminal 1: python -m backend.main
2. Terminal 2: python -m consumer.plate_analysis_consumer
3. Terminal 3: curl -X POST http://localhost:8000/analyze ...
4. Sprawdzenie wyniku w DB
```

### Scenariusz 4: Extended Scope (5 min)
```
1. python run_camera_monitor.py
2. Naciśnij 'q' aby zatrzymać
3. Sprawdzenie zapisanych wyników w DB
```

---

## Minimalne wymagania muszą być spełnione

| Wymóg | Status | Wartość |
|-------|--------|---------|
| Dokładność | ✓ | min 60% |
| Czas (100 zdjęć) | ✓ | max 60s |
| Test (min 30% datasetu) | ✓ | 59/195 = 30% |
| Ocena | ✓ | 2.0-5.0 |
| Branch | ✓ | automatic_plate_number_recognition |

---

## Przygotowanie do prezentacji

1. **Przed egzaminem**:
   - Zainstaluj zależności: `pip install -r requirements.txt`
   - Test: `python quick_test.py`
   - Sprawdź że API startuje: `python -m backend.main`

2. **Podczas prezentacji**:
   - Pokaż plik `CHECKLIST.md` - wszystkie wymagania spełnione
   - Uruchom ewaluację
   - Pokaż kod w edytorze
   - Wyjaśnij architekturę

3. **Problemy**:
   - Brak kamery? OK - extended scope opcjonalny
   - Niska dokładność? Normalne, zależy od dataset + modelu
   - Błędy? Sprawdź czy wszystkie dependencies zainstalowane

---

## Uwagi dla egzaminatora

- Projekt w Python 3.8+
- FastAPI + EasyOCR
- Dataset: 195 zdjęć z adnotacjami XML
- Każde zdjęcie ~0.2-0.5s przetwarzania
- 100 zdjęć = ~20-50s (poniżej limitu 60s)
- Ocena końcowa dynamicznie wyliczana
- Baza danych SQLite (lokalnie)
- Queue system: Redis (domyślnie)

---

**Projekt jest gotowy do oceny!**

---

*Wszelkie pytania - patrz TECHNICAL.md*
