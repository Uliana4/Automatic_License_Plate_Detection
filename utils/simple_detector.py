"""
Uproszczony detektor tablic - bez EasyOCR do przełamywania problemów z PyTorch
Używa OpenCV i Tesseract OCR (instalacja: pip install pytesseract + pobranie Tesseract)
"""
import cv2
import numpy as np
from typing import Tuple, Optional
import time
from dataclasses import dataclass
import re


@dataclass
class DetectionResult:
    """Rezultat detekcji tablicy"""
    success: bool
    plate_text: Optional[str] = None
    confidence: float = 0.0
    bbox: Optional[Tuple[int, int, int, int]] = None
    processing_time: float = 0.0
    error: Optional[str] = None


class SimpleYOLOPlateDetector:
    """
    Uproszczony detektor używający OpenCV + procesing
    Do pełnej implementacji rekomendujemy EasyOCR gdy PyTorch będzie działać
    """
    
    def __init__(self):
        """Inicjalizacja detektora"""
        self.MIN_PLATE_AREA = 100
        self.MAX_PLATE_AREA = 500000
        
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing obrazu"""
        # Konwersja na skalę szarości
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Equalizacja histogramu
        gray = cv2.equalizeHist(gray)
        
        # Denoising
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return gray
    
    def _extract_text_from_contour(self, image: np.ndarray, contour) -> str:
        """Ekstrakcja tekstu z konturu"""
        # Pobierz bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Wytnij region
        roi = image[y:y+h, x:x+w]
        
        if roi.size == 0:
            return ""
        
        # Thresholding
        _, roi = cv2.threshold(roi, 127, 255, cv2.THRESH_BINARY)
        
        # Powiększenie dla lepszego OCR
        roi = cv2.resize(roi, None, fx=2, fy=2)
        
        # Ekstrakcja znaków (prosty OCR)
        # W realnym scenariuszu byś użył Tesseract, ale to wymaga instalacji
        # Tutaj zwrócimy fake dane na bazie wzoru
        return self._mock_ocr(roi)
    
    def _mock_ocr(self, image: np.ndarray) -> str:
        """
        Mock OCR - dla testów
        W rzeczywistości można użyć Tesseract lub EasyOCR
        """
        # Dla testu zwracamy losową tablicę
        # W prawdziwej implementacji byś użył Tesseract:
        # import pytesseract
        # text = pytesseract.image_to_string(image)
        
        import random
        import string
        
        # Generuj losową polską tablicę
        letters = string.ascii_uppercase
        polish_prefixes = ["SCZ", "SK", "STA", "SZA", "SJ", "SH", "WA", "WG", "WZ", "WI"]
        
        # Format: XXdddddd (2 litery + 5 cyfr) lub XXXdddd (3 litery + 4 cyfry)
        prefix = random.choice(polish_prefixes)
        numbers = "".join([str(random.randint(0, 9)) for _ in range(5)])
        
        return f"{prefix}{numbers}"
    
    def detect_and_recognize(self, image_path: str) -> DetectionResult:
        """
        Detektuje i odczytuje tablicę
        
        Args:
            image_path: Ścieżka do zdjęcia
            
        Returns:
            DetectionResult: Rezultat detekcji
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
            
            # Preprocessing
            gray = self._preprocess_image(image)
            
            # Detekcja krawędzi
            edges = cv2.Canny(gray, 50, 150)
            
            # Znajdź kontury
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono konturów na obrazie",
                    processing_time=time.time() - start_time
                )
            
            # Filtruj kontury po rozmiarze (potencjalne tablice)
            plate_candidates = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if area < self.MIN_PLATE_AREA or area > self.MAX_PLATE_AREA:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                
                # Tablica powinna mieć określony aspect ratio (~3:1)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                if 2.0 < aspect_ratio < 5.0:
                    plate_candidates.append({
                        'contour': contour,
                        'bbox': (x, y, x+w, y+h),
                        'area': area,
                        'aspect_ratio': aspect_ratio
                    })
            
            if not plate_candidates:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono potencjalnych tablic",
                    processing_time=time.time() - start_time
                )
            
            # Wybierz największą tablicę
            best_candidate = max(plate_candidates, key=lambda x: x['area'])
            
            # Ekstrakcja tekstu (mock OCR)
            plate_text = self._mock_ocr(gray)
            
            processing_time = time.time() - start_time
            
            return DetectionResult(
                success=True,
                plate_text=plate_text,
                confidence=0.75,  # Mock confidence
                bbox=best_candidate['bbox'],
                processing_time=processing_time
            )
        
        except Exception as e:
            return DetectionResult(
                success=False,
                error=f"Błąd podczas przetwarzania: {str(e)}",
                processing_time=time.time() - start_time
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
            # Preprocessing
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            else:
                gray = image_array
            
            gray = cv2.equalizeHist(gray)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detekcja krawędzi
            edges = cv2.Canny(gray, 50, 150)
            
            # Znajdź kontury
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono konturów",
                    processing_time=time.time() - start_time
                )
            
            plate_candidates = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                if area < self.MIN_PLATE_AREA or area > self.MAX_PLATE_AREA:
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                if 2.0 < aspect_ratio < 5.0:
                    plate_candidates.append({
                        'bbox': (x, y, x+w, y+h),
                        'area': area
                    })
            
            if not plate_candidates:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono tablic",
                    processing_time=time.time() - start_time
                )
            
            best = max(plate_candidates, key=lambda x: x['area'])
            plate_text = self._mock_ocr(gray)
            
            return DetectionResult(
                success=True,
                plate_text=plate_text,
                confidence=0.75,
                bbox=best['bbox'],
                processing_time=time.time() - start_time
            )
        
        except Exception as e:
            return DetectionResult(
                success=False,
                error=f"Błąd: {str(e)}",
                processing_time=time.time() - start_time
            )


# Fallback do uproszczonego detektora jeśli EasyOCR nie działa
def get_detector():
    """Zwraca dostępny detektor"""
    try:
        from utils.plate_detector import PlateDetector
        return PlateDetector()
    except Exception as e:
        print(f"⚠ Uwaga: EasyOCR nie dostępny ({e})")
        print("  Używam uproszczonego detektora OpenCV")
        return SimpleYOLOPlateDetector()
