"""
Skrypt do szybkiego testu - ewaluuje kilka zdjęć
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import config
from utils.annotation_parser import AnnotationParser
from utils.evaluation import Evaluator
import os

# Fallback: użyj uproszczonego detektora jeśli EasyOCR nie działa
# Spróbuj załadować EasyOCR, ale przejdź na OpenCV jeśli problemy
use_simple = True  # Zmień na True aby wymusić OpenCV
if not use_simple:
    try:
        from utils.plate_detector import PlateDetector
        detector = PlateDetector(languages=config.OCR_LANGUAGES)
        print("Inicjalizacja: EasyOCR")
    except Exception as e:
        print(f"⚠ EasyOCR niedostępny, używam OpenCV")
        from utils.simple_detector import SimpleYOLOPlateDetector
        detector = SimpleYOLOPlateDetector()
else:
    print("Konfiguracja: Uzywam OpenCV (szybsze, bardziej stabilne)")
    from utils.simple_detector import SimpleYOLOPlateDetector
    detector = SimpleYOLOPlateDetector()

print("=" * 60)
print("QUICK TEST - Ewaluacja pierwszych 5 zdjęć")
print("=" * 60)

# Wczytaj adnotacje
parser = AnnotationParser(config.ANNOTATIONS_FILE)
annotations = parser.get_annotations()[:5]  # Pierwsze 5

print(f"Testowanie na {len(annotations)} zdjęciach\n")

evaluator = Evaluator()

photos_dir = config.PHOTOS_DIR

for idx, annotation in enumerate(annotations, 1):
    image_path = os.path.join(photos_dir, annotation.image_name)
    
    if not os.path.exists(image_path):
        print(f"[{idx}] ✗ {annotation.image_name} - plik nie znaleziony")
        continue
    
    result = detector.detect_and_recognize(image_path)
    
    if result.success:
        evaluator.add_result(
            predicted_plate=result.plate_text,
            ground_truth_plate=annotation.plate_number,
            predicted_bbox=result.bbox,
            ground_truth_bbox=annotation.bbox,
            processing_time=result.processing_time
        )
        
        match = "✓" if result.plate_text.upper() == annotation.plate_number.upper() else "✗"
        print(f"[{idx}] ✓ {annotation.image_name:20s} → {result.plate_text:15s} {match}")
    else:
        print(f"[{idx}] ✗ {annotation.image_name:20s} → Błąd: {result.error}")

print("\n" + "=" * 60)
evaluator.print_report()
