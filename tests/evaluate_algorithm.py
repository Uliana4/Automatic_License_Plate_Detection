"""
Skrypt do ewaluacji algorytmu na zestawie testowym
"""
import os
import sys
import time
from pathlib import Path

# Dodaj główny folder do ścieżki
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import config
from utils.annotation_parser import AnnotationParser
from utils.plate_detector import PlateDetector
from utils.evaluation import Evaluator


def evaluate_on_dataset(test_split: float = 0.3, num_samples: int = None):
    """
    Ewaluuje algorytm na zbiorze danych
    
    Args:
        test_split: Procent danych do testowania (0-1)
        num_samples: Liczba próbek do testowania (jeśli None, używaj wszystkie)
    """
    print("=" * 60)
    print("EWALUACJA ALGORYTMU DETEKCJI TABLIC")
    print("=" * 60)
    
    # Wczytaj adnotacje
    annotations_path = config.ANNOTATIONS_FILE
    if not os.path.exists(annotations_path):
        print(f"Błąd: Plik adnotacji nie znaleziony: {annotations_path}")
        return
    
    parser = AnnotationParser(annotations_path)
    all_annotations = parser.get_annotations()
    
    print(f"Całkowita liczba adnotacji: {len(all_annotations)}")
    
    # Przygotuj zbiór testowy
    num_test = max(1, int(len(all_annotations) * test_split))
    if num_samples:
        num_test = min(num_test, num_samples)
    
    test_annotations = all_annotations[:num_test]
    print(f"Liczba obrazów do testowania: {num_test}")
    print(f"Split: {test_split * 100}% (minimum 30%)")
    
    # Inicjalizuj detektor i ewaluator
    detector = PlateDetector(languages=config.OCR_LANGUAGES)
    evaluator = Evaluator()
    
    # Testuj na zbiorze
    photos_dir = config.PHOTOS_DIR
    
    print("\nRozpoczęcie testowania...")
    print("-" * 60)
    
    successful_detections = 0
    
    for idx, annotation in enumerate(test_annotations, 1):
        image_path = os.path.join(photos_dir, annotation.image_name)
        
        if not os.path.exists(image_path):
            print(f"[{idx}/{num_test}] ✗ {annotation.image_name} - plik nie znaleziony")
            continue
        
        # Przeprowadź detekcję
        result = detector.detect_and_recognize(image_path)
        
        if result.success:
            successful_detections += 1
            status = "✓"
        else:
            status = "✗"
        
        # Dodaj do ewaluatora
        if result.success:
            evaluator.add_result(
                predicted_plate=result.plate_text,
                ground_truth_plate=annotation.plate_number,
                predicted_bbox=result.bbox,
                ground_truth_bbox=annotation.bbox,
                processing_time=result.processing_time
            )
            
            match = "✓" if result.plate_text.upper() == annotation.plate_number.upper() else "✗"
            print(f"[{idx}/{num_test}] {status} {annotation.image_name:20s} "
                  f"→ {result.plate_text:15s} (actual: {annotation.plate_number}) {match}")
        else:
            print(f"[{idx}/{num_test}] {status} {annotation.image_name:20s} "
                  f"→ Błąd: {result.error}")
    
    # Pokaż rezultaty
    print("-" * 60)
    metrics = evaluator.get_metrics()
    
    if metrics:
        evaluator.print_report()
    else:
        print("Nie udało się przeprowadzić żadnej detekcji.")
        return
    
    # Dodatkowe informacje
    print("\nDETALE OCENY:")
    print(f"Minimalna dokładność wymagana: 60%")
    print(f"Maksymalny czas przetwarzania 100 zdjęć: 60 sekund")
    print(f"Waga dokładności: 0.7")
    print(f"Waga czasu: 0.3")
    print("\nJeśli masz 100 zdjęć:")
    time_for_100 = (metrics['total_processing_time_sec'] / len(test_annotations)) * 100
    print(f"Szacunkowy czas dla 100 zdjęć: {time_for_100:.2f}s")
    

def evaluate_100_images():
    """
    Ewaluuje algorytm na 100 zdjęciach (jeśli dostępnych)
    """
    print("=" * 60)
    print("EWALUACJA NA 100 ZDJĘCIACH")
    print("=" * 60)
    
    # Wczytaj adnotacje
    annotations_path = config.ANNOTATIONS_FILE
    if not os.path.exists(annotations_path):
        print(f"Błąd: Plik adnotacji nie znaleziony: {annotations_path}")
        return
    
    parser = AnnotationParser(annotations_path)
    all_annotations = parser.get_annotations()
    
    # Weź do 100 zdjęć
    num_samples = min(100, len(all_annotations))
    test_annotations = all_annotations[:num_samples]
    
    print(f"Dostępnych adnotacji: {len(all_annotations)}")
    print(f"Testowanie na: {num_samples} zdjęciach")
    
    # Inicjalizuj detektor i ewaluator
    detector = PlateDetector(languages=config.OCR_LANGUAGES)
    evaluator = Evaluator()
    
    # Testuj na zbiorze
    photos_dir = config.PHOTOS_DIR
    
    print("\nRozpoczęcie testowania...")
    print("-" * 60)
    
    for idx, annotation in enumerate(test_annotations, 1):
        image_path = os.path.join(photos_dir, annotation.image_name)
        
        if not os.path.exists(image_path):
            print(f"[{idx}/{num_samples}] ✗ {annotation.image_name} - plik nie znaleziony")
            continue
        
        # Przeprowadź detekcję
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
            print(f"[{idx}/{num_samples}] ✓ {annotation.image_name:20s} "
                  f"→ {result.plate_text:15s} (actual: {annotation.plate_number}) {match}")
        else:
            print(f"[{idx}/{num_samples}] ✗ {annotation.image_name:20s} "
                  f"→ Błąd: {result.error}")
    
    # Pokaż rezultaty
    print("-" * 60)
    metrics = evaluator.get_metrics()
    
    if metrics:
        evaluator.print_report()
    else:
        print("Nie udało się przeprowadzić żadnej detekcji.")


if __name__ == "__main__":
    # Ewaluacja na 30% zestawu (minimum wymagane)
    evaluate_on_dataset(test_split=0.3)
    
    print("\n" * 2)
    
    # Jeśli mamy 100+ zdjęć, przeprowadź dodatkową ewaluację
    if len(AnnotationParser(config.ANNOTATIONS_FILE).get_annotations()) >= 100:
        evaluate_100_images()
