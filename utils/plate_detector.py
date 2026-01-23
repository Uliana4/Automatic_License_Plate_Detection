"""
Moduł OCR i detekcji tablic rejestracyjnych
"""
import cv2
import easyocr
import numpy as np
from typing import Tuple, List, Dict, Optional
import time
from dataclasses import dataclass


@dataclass
class DetectionResult:
    """Rezultat detekcji tablicy"""
    success: bool
    plate_text: Optional[str] = None
    confidence: float = 0.0
    bbox: Optional[Tuple[int, int, int, int]] = None
    processing_time: float = 0.0
    error: Optional[str] = None


class PlateDetector:
    """Detektor i czytnik tablic rejestracyjnych"""
    
    def __init__(self, languages=['en']):
        """
        Inicjalizacja detektora
        
        Args:
            languages: Języki do OCR
        """
        self.reader = easyocr.Reader(languages, gpu=False)
    
    def detect_and_recognize(self, image_path: str) -> DetectionResult:
        """
        Detektuje i odczytuje tablicę rejestracyjną
        
        Args:
            image_path: Ścieżka do zdjęcia
            
        Returns:
            DetectionResult: Rezultat detekcji i OCR
        """
        start_time = time.time()
        
        try:
            # Wczytaj obraz
            image = cv2.imread(image_path)
            if image is None:
                return DetectionResult(
                    success=False,
                    error=f"Nie można wczytać obrazu: {image_path}",
                    processing_time=time.time() - start_time
                )
            
            # Konwersja do RGB dla EasyOCR
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detektuj tekst za pomocą EasyOCR
            results = self.reader.readtext(image_rgb)
            
            if not results:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono tekstu na obrazie",
                    processing_time=time.time() - start_time
                )
            
            # Filtruj wyniki - szukaj tekstu o odpowiedniej długości (tablica rejestracyjna)
            plate_candidates = []
            
            for (bbox, text, confidence) in results:
                # Tablica powinna mieć 7-8 znaków (np. SCZ26114)
                text_clean = text.replace(' ', '').replace('-', '')
                if 6 <= len(text_clean) <= 10 and confidence > 0.3:
                    # Konwertuj współrzędne bbox
                    points = np.array(bbox, dtype=np.int32)
                    x_min = int(np.min(points[:, 0]))
                    y_min = int(np.min(points[:, 1]))
                    x_max = int(np.max(points[:, 0]))
                    y_max = int(np.max(points[:, 1]))
                    
                    plate_candidates.append({
                        'text': text_clean,
                        'confidence': confidence,
                        'bbox': (x_min, y_min, x_max, y_max),
                        'area': (x_max - x_min) * (y_max - y_min)
                    })
            
            if not plate_candidates:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono tekstu podobnego do tablicy",
                    processing_time=time.time() - start_time
                )
            
            # Wybierz największy tekst (najczęściej będzie to tablica)
            best_candidate = max(plate_candidates, key=lambda x: x['area'])
            
            processing_time = time.time() - start_time
            
            return DetectionResult(
                success=True,
                plate_text=best_candidate['text'],
                confidence=best_candidate['confidence'],
                bbox=best_candidate['bbox'],
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return DetectionResult(
                success=False,
                error=f"Błąd podczas przetwarzania: {str(e)}",
                processing_time=processing_time
            )
    
    def detect_from_array(self, image_array: np.ndarray) -> DetectionResult:
        """
        Detektuje tablicę z numpy array
        
        Args:
            image_array: Obraz jako numpy array
            
        Returns:
            DetectionResult: Rezultat detekcji
        """
        start_time = time.time()
        
        try:
            # Jeśli obraz jest w BGR, konwertuj na RGB
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image_array
            
            results = self.reader.readtext(image_rgb)
            
            if not results:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono tekstu na obrazie",
                    processing_time=time.time() - start_time
                )
            
            plate_candidates = []
            
            for (bbox, text, confidence) in results:
                text_clean = text.replace(' ', '').replace('-', '')
                if 6 <= len(text_clean) <= 10 and confidence > 0.3:
                    points = np.array(bbox, dtype=np.int32)
                    x_min = int(np.min(points[:, 0]))
                    y_min = int(np.min(points[:, 1]))
                    x_max = int(np.max(points[:, 0]))
                    y_max = int(np.max(points[:, 1]))
                    
                    plate_candidates.append({
                        'text': text_clean,
                        'confidence': confidence,
                        'bbox': (x_min, y_min, x_max, y_max),
                        'area': (x_max - x_min) * (y_max - y_min)
                    })
            
            if not plate_candidates:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono tekstu podobnego do tablicy",
                    processing_time=time.time() - start_time
                )
            
            best_candidate = max(plate_candidates, key=lambda x: x['area'])
            
            processing_time = time.time() - start_time
            
            return DetectionResult(
                success=True,
                plate_text=best_candidate['text'],
                confidence=best_candidate['confidence'],
                bbox=best_candidate['bbox'],
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return DetectionResult(
                success=False,
                error=f"Błąd podczas przetwarzania: {str(e)}",
                processing_time=processing_time
            )
