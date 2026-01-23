"""
Metryki ewaluacyjne
"""
import time
from typing import List, Tuple, Dict
import numpy as np


def calculate_iou(box1: Tuple[float, float, float, float], 
                  box2: Tuple[float, float, float, float]) -> float:
    """
    Oblicza Intersection over Union (IoU) dla dwóch bounding boxów
    
    Args:
        box1: Pierwszy box (xtl, ytl, xbr, ybr)
        box2: Drugi box (xtl, ytl, xbr, ybr)
    
    Returns:
        float: IoU wartość (0-1)
    """
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    # Intersection
    xi_min = max(x1_min, x2_min)
    yi_min = max(y1_min, y2_min)
    xi_max = min(x1_max, x2_max)
    yi_max = min(y1_max, y2_max)
    
    if xi_max < xi_min or yi_max < yi_min:
        return 0.0
    
    intersection_area = (xi_max - xi_min) * (yi_max - yi_min)
    
    # Union
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = box1_area + box2_area - intersection_area
    
    if union_area == 0:
        return 0.0
    
    return intersection_area / union_area


def calculate_accuracy(predicted_plates: List[str], 
                      ground_truth_plates: List[str]) -> float:
    """
    Oblicza dokładność (accuracy) odczytu tablic
    
    Args:
        predicted_plates: Lista przewidzianych numerów tablic
        ground_truth_plates: Lista rzeczywistych numerów tablic
    
    Returns:
        float: Dokładność w procentach (0-100)
    """
    if len(ground_truth_plates) == 0:
        return 0.0
    
    correct = sum(1 for pred, true in zip(predicted_plates, ground_truth_plates) 
                  if pred.upper() == true.upper())
    
    return (correct / len(ground_truth_plates)) * 100


def calculate_processing_time(times: List[float]) -> float:
    """
    Oblicza średni czas przetwarzania
    
    Args:
        times: Lista czasów przetwarzania
    
    Returns:
        float: Całkowity czas w sekundach
    """
    return sum(times)


def calculate_final_grade(accuracy_percent: float, processing_time_sec: float) -> float:
    """
    Oblicza ocenę końcową na podstawie dokładności i czasu przetwarzania
    
    Wymaga:
    - Minimum dokładności: 60%
    - Maksymalny czas przetwarzania: 60s
    
    Args:
        accuracy_percent: Dokładność OCR w procentach (0-100)
        processing_time_sec: Całkowity czas przetwarzania 100 zdjęć w sekundach
    
    Returns:
        float: Ocena na skali 2.0-5.0 (zaokrąglona do 0.5)
    """
    # Sprawdzenie minimalne wymagań
    if accuracy_percent < 60 or processing_time_sec > 60:
        return 2.0
    
    # Normalizacja dokładności: 60% → 0.0, 100% → 1.0
    accuracy_norm = (accuracy_percent - 60) / 40
    # Normalizacja czasu: 60s → 0.0, 10s → 1.0
    time_norm = (60 - processing_time_sec) / 50
    
    # Obliczenie ważonego wyniku
    score = 0.7 * accuracy_norm + 0.3 * time_norm
    grade = 2.0 + 3.0 * score
    
    # Zaokrąglenie do 0.5
    return round(grade * 2) / 2


class Evaluator:
    """Ewaluator wydajności algorytmu"""
    
    def __init__(self):
        self.results = []
        self.processing_times = []
    
    def add_result(self, predicted_plate: str, ground_truth_plate: str, 
                   predicted_bbox: Tuple[float, float, float, float],
                   ground_truth_bbox: Tuple[float, float, float, float],
                   processing_time: float) -> None:
        """
        Dodaje wynik
        
        Args:
            predicted_plate: Przewidziana tablica
            ground_truth_plate: Rzeczywista tablica
            predicted_bbox: Przewidziany bounding box
            ground_truth_bbox: Rzeczywisty bounding box
            processing_time: Czas przetwarzania
        """
        iou = calculate_iou(predicted_bbox, ground_truth_bbox)
        match = predicted_plate.upper() == ground_truth_plate.upper()
        
        self.results.append({
            'predicted_plate': predicted_plate,
            'ground_truth_plate': ground_truth_plate,
            'match': match,
            'iou': iou,
            'processing_time': processing_time
        })
        self.processing_times.append(processing_time)
    
    def get_metrics(self) -> Dict:
        """
        Zwraca metryki ewaluacyjne
        
        Returns:
            Dict: Słownik z metrykami
        """
        if not self.results:
            return {}
        
        correct_plates = sum(1 for r in self.results if r['match'])
        accuracy = (correct_plates / len(self.results)) * 100
        
        avg_iou = np.mean([r['iou'] for r in self.results])
        total_time = sum(self.processing_times)
        avg_time = np.mean(self.processing_times)
        
        final_grade = calculate_final_grade(accuracy, total_time)
        
        return {
            'total_images': len(self.results),
            'correct_plates': correct_plates,
            'accuracy_percent': accuracy,
            'avg_iou': avg_iou,
            'total_processing_time_sec': total_time,
            'avg_processing_time_sec': avg_time,
            'final_grade': final_grade
        }
    
    def print_report(self) -> None:
        """Wypisuje raport z metrykami"""
        metrics = self.get_metrics()
        
        print("=" * 60)
        print("RAPORT EWALUACJI ALGORYTMU DETEKCJI TABLIC")
        print("=" * 60)
        print(f"Całkowita liczba zdjęć: {metrics['total_images']}")
        print(f"Poprawnie odczytane tablice: {metrics['correct_plates']}")
        print(f"Dokładność (Accuracy): {metrics['accuracy_percent']:.2f}%")
        print(f"Średnia miara IoU: {metrics['avg_iou']:.4f}")
        print(f"Całkowity czas przetwarzania: {metrics['total_processing_time_sec']:.2f}s")
        print(f"Średni czas na zdjęcie: {metrics['avg_processing_time_sec']:.4f}s")
        print(f"\nOCENA KOŃCOWA: {metrics['final_grade']:.1f}")
        print("=" * 60)
