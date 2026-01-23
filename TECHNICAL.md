# Dokumentacja Techniczna

## Architektura systemu

```
┌─────────────────┐
│   API Client    │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  FastAPI │
    │ Backend  │
    └────┬─────┘
         │
    ┌────▼────────────┐
    │ Queue Manager   │
    │ (Redis/RabbitMQ)│
    └────┬────────────┘
         │
    ┌────▼─────────┐
    │  Consumer    │
    │ (async)      │
    └────┬─────────┘
         │
    ┌────▼─────────────────┐
    │  Plate Detector      │
    │ (EasyOCR)            │
    └────┬─────────────────┘
         │
    ┌────▼─────────┐
    │  Database    │
    │ (SQLite)     │
    └──────────────┘
```

## Komponenty

### 1. Backend (FastAPI)
- **Plik**: `backend/main.py`
- **Port**: 8000
- **Endpoints**:
  - `POST /analyze` - Bezpośrednia analiza
  - `POST /queue-analysis` - Dodanie do kolejki
  - `GET /queue-status` - Status kolejki

### 2. Queue Manager
- **Plik**: `backend/queue_manager.py`
- **Obsługiwane systemy**:
  - Redis (domyślnie) - szybki, in-memory
  - RabbitMQ - bardziej niezawodny, persistentny
  - SQLite - fallback bez dodatkowych zależności

### 3. Consumer
- **Plik**: `consumer/plate_analysis_consumer.py`
- **Funkcja**: Czyta z kolejki i analizuje zdjęcia
- **Output**: Zapisuje wyniki w bazie danych

### 4. Plate Detector
- **Plik**: `utils/plate_detector.py`
- **Technologia**: EasyOCR
- **Języki**: Polski (en), można rozszerzać

### 5. Database
- **Plik**: `backend/database.py`
- **Typ**: SQLite (domyślnie)
- **Tabela**: `plate_results`

## Algorytm detekcji

### EasyOCR Pipeline

```
Image Input
    ↓
[EasyOCR Reader]
    ├─ Text Detection (CRAFT)
    ├─ Text Recognition (CRNN)
    └─ Filter Results (length 6-10 chars)
    ↓
[Bbox Selection]
    └─ Select largest text area
    ↓
Output: Plate Number + Confidence
```

### Optymalizacje

1. **Filtrowanie**:
   - Długość tekstu: 6-10 znaków (tablice polskie: 7-8)
   - Confidence threshold: 0.3

2. **Preprocessing** (advanced_detector.py):
   - CLAHE (Contrast Limited Adaptive Histogram Equalization)
   - Thresholding (OTSU)
   - Resizing do maksymalnie 1920px

## Metryki ewaluacyjne

### 1. Dokładność (Accuracy)
```
Accuracy = (Correct Predictions) / (Total Samples) * 100%
```

### 2. Intersection over Union (IoU)
```
IoU = Area(Intersection) / Area(Union)

Intersection: x_min = max(x1_min, x2_min), ... (analogicznie dla każdej osi)
Union: Area1 + Area2 - Intersection
```

### 3. Czas przetwarzania
```
Total Time = Σ(time_per_image)
Avg Time = Total Time / Number of Images
```

### 4. Ocena końcowa

```python
def calculate_final_grade(accuracy, time):
    if accuracy < 60 or time > 60:
        return 2.0
    
    accuracy_norm = (accuracy - 60) / 40      # [0, 1]
    time_norm = (60 - time) / 50               # [0, 1]
    
    score = 0.7 * accuracy_norm + 0.3 * time_norm
    grade = 2.0 + 3.0 * score
    
    return round(grade * 2) / 2  # Zaokrąglenie do 0.5
```

## Konfiguracja

### Plik .env

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Database
DATABASE_URL=sqlite:///./database.db

# Queue System
QUEUE_SYSTEM=redis  # lub rabbitmq
```

## Performance Tips

### 1. Batch Processing
```python
# Przetwarzaj wiele zdjęć naraz
for images in batch_generator(image_list, batch_size=32):
    results = detector.detect_batch(images)
```

### 2. GPU Acceleration
```python
# Użycie GPU (jeśli dostępne)
detector = PlateDetector()
detector.reader.cuda_enabled = True
```

### 3. Model Caching
```python
# EasyOCR cachuje modele domyślnie w ~/.EasyOCR/
# Można zmienić: export EASYOCR_HOME=/custom/path
```

## Błędy i rozwiązania

| Błąd | Przyczyna | Rozwiązanie |
|------|-----------|------------|
| `ModuleNotFoundError: easyocr` | Brak EasyOCR | `pip install easyocr` |
| `ConnectionError: Redis` | Redis niedostępny | Zainstaluj Redis lub zmień QUEUE_SYSTEM |
| `OutOfMemory` | Za duży batch | Zmniejsz BATCH_SIZE w config |
| `Low accuracy` | Słaba jakość zdjęć | Użyj advanced_detector preprocessing |

## Dane testowe

Dataset: Poland Vehicle License Plate Dataset (Kaggle)
- **Liczba zdjęć**: 195
- **Format adnotacji**: XML (CVAT)
- **Zawartość**: Numery tablic + bounding boxy

## Ścieżka rozwoju

### Faza 1 ✓ (obecna)
- Podstawowa detekcja EasyOCR
- API + Queue System
- Ewaluacja metryk

### Faza 2 (opcjonalnie)
- Wdrożenie YOLO dla lepszej detekcji
- Trenowanie na własnym datasecie
- Integracja z kamerą

### Faza 3 (extended scope)
- Ciągły monitoring z kamery
- Real-time alerting
- Dashboard UI

## Zmienne środowiska

| Zmienna | Domyślna | Opis |
|---------|----------|------|
| `REDIS_HOST` | localhost | Host Redis |
| `REDIS_PORT` | 6379 | Port Redis |
| `QUEUE_SYSTEM` | redis | System kolejek |
| `DATABASE_URL` | sqlite | URL bazy danych |
| `OCR_LANGUAGES` | en | Języki dla OCR |
| `DETECTION_CONFIDENCE` | 0.5 | Threshold pewności |

## Zasoby

- **EasyOCR Docs**: https://github.com/JaidedAI/EasyOCR
- **FastAPI**: https://fastapi.tiangolo.com
- **Redis**: https://redis.io
- **RabbitMQ**: https://www.rabbitmq.com

## Licencja

Projekt edukacyjny na potrzeby zaliczenia.
