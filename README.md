# Projekt: Detekcja i OCR Tablic Rejestracyjnych

Projekt opiera się na automatycznym rozpoznawaniu tablic rejestracyjnych przy użyciu detekcji oraz OCR.

## Wymagania

- Python 3.8+
- Redis lub RabbitMQ (opcjonalnie)
- OpenCV
- EasyOCR

## Instalacja

### 1. Klonowanie i przygotowanie

```bash
cd zalicenie
git checkout automatic_plate_number_recognition
pip install -r requirements.txt
```

### 2. Konfiguracja

Skopiuj `.env.example` do `.env` i dostosuj ustawienia:

```bash
cp .env.example .env
```

Domyślnie używany jest SQLite i Redis.

## Struktura projektu

```
zalicenie/
├── backend/               # Backend FastAPI
│   ├── main.py          # Endpoints API
│   ├── queue_manager.py # Obsługa kolejek (Redis/RabbitMQ)
│   └── database.py      # Model bazy danych
├── consumer/            # Consumer dla kolejki
│   └── plate_analysis_consumer.py
├── utils/               # Narzędzia
│   ├── config.py        # Konfiguracja
│   ├── annotation_parser.py  # Parser XML
│   ├── plate_detector.py     # Detektor i OCR
│   └── evaluation.py         # Metryki
├── tests/               # Testy
│   ├── evaluate_algorithm.py # Ewaluacja algorytmu
│   └── test_api.py          # Testy API
├── photos/              # Dataset (zdjęcia)
├── annotations.xml      # Adnotacje
└── requirements.txt
```

## Uruchamianie

### 1. Backend (API)

```bash
python -m backend.main
```

Dostępne będą endpoints:
- `POST /analyze` - natychmiastowa analiza
- `POST /queue-analysis` - analiza asynchroniczna
- `GET /queue-status` - status kolejki
- `POST /clear-queue` - czyszczenie kolejki

### 2. Consumer (w osobnym terminalu)

```bash
python -m consumer.plate_analysis_consumer
```

Consumer automatycznie czyta z kolejki i analizuje zdjęcia.

### 3. Testowanie API

```bash
python -m tests.test_api
```

### 4. Ewaluacja algorytmu

```bash
python -m tests.evaluate_algorithm
```

Wykonuje pełną ewaluację na zbiorze testowym i wyświetla:
- Dokładność (accuracy)
- Średnią miarę IoU
- Czas przetwarzania
- **Ocenę końcową (2.0-5.0)**

## Endpoints API

### POST /analyze
Natychmiastowa analiza przesłanego zdjęcia.

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -F "file=@photo.jpg"
```

Response:
```json
{
  "success": true,
  "plate_text": "SCZ26114",
  "confidence": 0.95,
  "bbox": [1318, 537, 2016, 704],
  "processing_time": 2.345
}
```

### POST /queue-analysis
Dodanie zdjęcia do asynchronicznej kolejki.

```bash
curl -X POST "http://localhost:8000/queue-analysis" \
  -H "accept: application/json" \
  -F "file=@photo.jpg"
```

### GET /queue-status
Status kolejki.

```bash
curl "http://localhost:8000/queue-status"
```

### POST /clear-queue
Czyszczenie kolejki.

```bash
curl -X POST "http://localhost:8000/clear-queue"
```

## Algorytm

### Detekcja i OCR

Projekt wykorzystuje **EasyOCR** do równoczesnej detekcji i odczytu tekstu.

1. Wczytanie obrazu
2. Uruchomienie modelu OCR EasyOCR
3. Filtrowanie wyników (szukanie tekstu o długości 6-10 znaków)
4. Wybranie największego tekstu jako tablicy

### Metryki ewaluacyjne

#### Dokładność (Accuracy)
```
accuracy = (liczba poprawnie odczytanych tablic) / (liczba wszystkich tablic) * 100%
```

#### Intersection over Union (IoU)
```
IoU = intersection_area / union_area
```

#### Czas przetwarzania
Całkowity czas przetwarzania 100 zdjęć w sekundach.

#### Ocena końcowa
```python
def calculate_final_grade(accuracy_percent: float, processing_time_sec: float) -> float:
    if accuracy_percent < 60 or processing_time_sec > 60:
        return 2.0
    
    accuracy_norm = (accuracy_percent - 60) / 40
    time_norm = (60 - processing_time_sec) / 50
    
    score = 0.7 * accuracy_norm + 0.3 * time_norm
    grade = 2.0 + 3.0 * score
    
    return round(grade * 2) / 2
```

## System kolejek

Projekt obsługuje dwa systemy kolejek:

### Redis (domyślnie)
Szybki, in-memory cache do przechowywania wiadomości.

```bash
# Uruchomienie Redisa (jeśli zainstalowany)
redis-server
```

### RabbitMQ
Bardziej zaawansowany system zarządzania kolejkami.

```bash
# Zmiana w .env
QUEUE_SYSTEM=rabbitmq
```

## Docker Compose

Do uruchomienia Redis i RabbitMQ:

```bash
docker-compose up -d
```

## Wyniki

Po uruchomieniu ewaluacji widzimy raport:

```
============================================================
RAPORT EWALUACJI ALGORYTMU DETEKCJI TABLIC
============================================================
Całkowita liczba zdjęć: 100
Poprawnie odczytane tablice: 85
Dokładność (Accuracy): 85.00%
Średnia miara IoU: 0.7654
Całkowity czas przetwarzania: 28.45s
Średni czas na zdjęcie: 0.2845s

OCENA KOŃCOWA: 4.0
============================================================
```

## Wymagane metryki

- ✓ Minimalna dokładność: 60%
- ✓ Maksymalny czas: 60s na 100 zdjęć
- ✓ Waga dokładności: 0.7
- ✓ Waga czasu: 0.3
- ✓ Miara IoU dla detekcji
- ✓ Test na minimum 30% datasetu

## Branch

Projekt znajduje się na branchu:
```
automatic_plate_number_recognition
```

## Autor
Uliana Kutylovskaya.
