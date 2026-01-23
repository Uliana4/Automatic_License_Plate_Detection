# Indeks plików projektu

## 📋 Dokumentacja

| Plik | Opis |
|------|------|
| **README.md** | Główny plik dokumentacji |
| **QUICK_START.md** | Szybki start (5 minut) |
| **TECHNICAL.md** | Dokumentacja techniczna |
| **CHECKLIST.md** | Lista wymagań - wszystkie ✓ |
| **EXAM_GUIDE.md** | Instrukcja dla egzaminatora |
| **INDEX.md** | Ten plik - przegląd struktury |

## 🔧 Główne komponenty

### Backend (`backend/`)
```
backend/
├── __init__.py          - Inicjalizacja modułu
├── main.py              - FastAPI serwer (2 endpoints)
│   └── /analyze         - Bezpośrednia analiza
│   └── /queue-analysis  - Dodanie do kolejki
├── queue_manager.py     - Obsługa kolejek (Redis/RabbitMQ)
└── database.py          - SQLite ORM, przechowywanie wyników
```

### Consumer (`consumer/`)
```
consumer/
├── __init__.py                      - Inicjalizacja
└── plate_analysis_consumer.py       - Asynchroniczne przetwarzanie
    ├── Czyta z kolejki
    ├── Analizuje zdjęcia
    └── Zapisuje wyniki w DB
```

### Narzędzia (`utils/`)
```
utils/
├── __init__.py              - Inicjalizacja
├── config.py                - Konfiguracja aplikacji
├── annotation_parser.py     - Parser XML z CVAT
├── plate_detector.py        - EasyOCR detektor + OCR
├── evaluation.py            - Metryki (accuracy, IoU, ocena)
├── advanced_detector.py     - YOLO (opcjonalnie)
└── camera_monitor.py        - Monitor z kamerą (Extended Scope)
```

### Testy (`tests/`)
```
tests/
├── __init__.py                  - Inicjalizacja
├── evaluate_algorithm.py        - Pełna ewaluacja na datasecie
│   ├── Test 30% datasetu
│   ├── Obliczanie metryki
│   └── Wynik oceny (2.0-5.0)
└── test_api.py                  - Testy endpoints API
```

## 🚀 Skrypty uruchomieniowe

| Plik | OS | Funkcja |
|------|----|----|
| **run_backend.bat** | Windows | Start API |
| **run_consumer.bat** | Windows | Start Consumera |
| **run_evaluation.bat** | Windows | Uruchom ewaluację |
| **run_system.sh** | Linux/Mac | Full system (wszystkie komponenty) |
| **quick_test.py** | All | Test na 5 zdjęciach |
| **run_camera_monitor.py** | All | Monitor z kamerą |

## 📊 Dataset

```
photos/                     - 195 zdjęć (samochody z tablicami)
annotations.xml             - Adnotacje CVAT (lokalizacja + numer)
```

## 📦 Konfiguracja

| Plik | Opis |
|------|------|
| **requirements.txt** | Zależności Python |
| **.env.example** | Przykład zmiennych środowiska |
| **.gitignore** | Ignorowane pliki dla git |
| **docker-compose.yml** | Konfiguracja Redis + RabbitMQ |

## 📝 Plik struktury projektu

```
zalicenie/
│
├── 📄 Dokumentacja
│   ├── README.md
│   ├── QUICK_START.md
│   ├── TECHNICAL.md
│   ├── CHECKLIST.md
│   ├── EXAM_GUIDE.md
│   └── INDEX.md (ten plik)
│
├── 🔧 Kod
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py (API)
│   │   ├── queue_manager.py
│   │   └── database.py
│   ├── consumer/
│   │   ├── __init__.py
│   │   └── plate_analysis_consumer.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── annotation_parser.py
│   │   ├── plate_detector.py (EasyOCR)
│   │   ├── evaluation.py (metryki)
│   │   ├── advanced_detector.py
│   │   └── camera_monitor.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── evaluate_algorithm.py
│   │   └── test_api.py
│   ├── quick_test.py
│   └── run_camera_monitor.py
│
├── 🚀 Skrypty
│   ├── run_backend.bat
│   ├── run_consumer.bat
│   ├── run_evaluation.bat
│   └── run_system.sh
│
├── 📊 Dataset
│   ├── photos/ (195 zdjęć)
│   └── annotations.xml (adnotacje)
│
└── ⚙️ Konfiguracja
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── docker-compose.yml
```

## 🎯 Funkcjonalność

### 1. Detekcja tablicy
- **Technologia**: EasyOCR
- **Plik**: `utils/plate_detector.py`
- **Funkcja**: Automatyczne wykrywanie i odczyt tablicy

### 2. Dwa warianty analizy
- **Synchroniczny**: `POST /analyze` - natychmiastowy wynik
- **Asynchroniczny**: `POST /queue-analysis` - zapisanie do kolejki

### 3. System kolejek
- **Redis** (domyślnie) - szybki, in-memory
- **RabbitMQ** - persistent, bardziej niezawodny
- **SQLite** - fallback (bez Redis/RabbitMQ)

### 4. Consumer
- Czyta z kolejki
- Analizuje asynchronicznie
- Zapisuje wyniki w bazie

### 5. Metryki ewaluacyjne
- **Dokładność** (Accuracy)
- **Intersection over Union** (IoU)
- **Czas przetwarzania**
- **Ocena końcowa** (2.0-5.0)

### 6. Extended Scope
- Monitor z kamerą
- Real-time detekcja
- Wielowątkowy (capture + process)

## 🔄 Przepływ danych

```
┌─────────────────┐
│ Zdjęcie         │
└────────┬────────┘
         │
    ┌────▼──────────────┐
    │ Endpoint API      │
    │ /analyze lub      │
    │ /queue-analysis   │
    └────────┬──────────┘
             │
         (sync)     (async)
          │           │
         ▼           ▼
    Direktna     Queue
    analiza      Manager
         │           │
         └─────┬─────┘
              ▼
      Plate Detector
      (EasyOCR)
              │
         ┌────▼─────┐
         │ Wynik:   │
         │ - tablica│
         │ - bbox   │
         │ - czas   │
         └────┬─────┘
              │
         Database
         (SQLite)
```

## 📈 Wyliczanie oceny

```python
# Jeśli accuracy < 60% lub czas > 60s
grade = 2.0

# W przeciwnym razie
accuracy_norm = (accuracy - 60) / 40        # [0, 1]
time_norm = (60 - time) / 50                # [0, 1]
score = 0.7 * accuracy_norm + 0.3 * time_norm
grade = 2.0 + 3.0 * score                   # [2.0, 5.0]

# Zaokrąglenie do 0.5
grade = round(grade * 2) / 2
```

## ✨ Przykładowe wyniki

```
Dokładność: 85%
Czas: 28s na 100 zdjęć
Wyliczona ocena: 4.0
```

## 📚 Używane biblioteki

| Biblioteka | Wersja | Funkcja |
|-----------|--------|---------|
| FastAPI | 0.104.1 | Backend API |
| EasyOCR | 1.7.0 | OCR + Detekcja |
| Redis | 5.0.1 | Queue (opcjonalnie) |
| Pika | 1.3.2 | RabbitMQ (opcjonalnie) |
| SQLAlchemy | 2.0.23 | Database ORM |
| OpenCV | 4.8.1.78 | Przetwarzanie obrazów |

## 🐛 Rozwiązywanie problemów

### Brak modelu EasyOCR
```bash
python -m easyocr --download-all  # Pobierz modele
```

### Redis niedostępny
```bash
# Zmień w .env lub redis-server
QUEUE_SYSTEM=sqlite
```

### Niska dokładność
- Spróbuj advanced_detector.py (preprocessing)
- Można trenować YOLO na własnym datasecie

## 🎓 Wymagania spełnione

✓ Detekcja tablicy  
✓ OCR  
✓ Dokładność + IoU + Czas  
✓ Ocena (2.0-5.0)  
✓ API + Queue  
✓ Consumer  
✓ Database  
✓ Test na 30% datasetu  
✓ Extended Scope (kamera)  
✓ Git branch  
✓ Dokumentacja  

**PROJEKT GOTOWY!**

---

*Data: 23 Stycznia 2026*  
*Branch: automatic_plate_number_recognition*
