"""
Detektor tablic rejestracyjnych - wersja 2.0
Używa: właściwa detekcja + REAL OCR (Tesseract/EasyOCR)
"""
import cv2
import numpy as np
from typing import Tuple, List, Dict, Optional
import time
from dataclasses import dataclass
import os

# Spróbuj załadować OCR Engine
try:
    from utils.ocr_engine import OCREngine
    OCRE_ENGINE_AVAILABLE = True
except ImportError:
    OCRE_ENGINE_AVAILABLE = False


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
    """
    Detektor i czytnik tablic rejestracyjnych
    Używa: detekcja krawędzi + heurystyka + REAL OCR (Tesseract/EasyOCR)
    """
    
    # Parametry detekcji
    MIN_PLATE_WIDTH = 100
    MIN_PLATE_HEIGHT = 30
    MAX_PLATE_WIDTH = 800
    MAX_PLATE_HEIGHT = 200
    MIN_ASPECT_RATIO = 2.0
    MAX_ASPECT_RATIO = 5.0
    
    def __init__(self, languages=['en']):
        """
        Inicjalizacja detektora
        
        Args:
            languages: Języki do OCR (dla EasyOCR)
        """
        self.languages = languages
        self.reader = None
        self.use_easyocr = False
        
        # Załaduj OCR Engine (wspiera Tesseract i EasyOCR)
        self.ocr_engine = None
        if OCRE_ENGINE_AVAILABLE:
            try:
                self.ocr_engine = OCREngine()
                print("[OK] OCR Engine zaladowany (Tesseract/EasyOCR)")
            except Exception as e:
                print(f"[WARN] OCR Engine inicjalizacja: {str(e)[:50]}")
        
        # Fallback: spróbuj załadować EasyOCR bezpośrednio
        if not self.ocr_engine:
            try:
                import easyocr
                self.reader = easyocr.Reader(languages, gpu=False)
                self.use_easyocr = True
                print("[OK] EasyOCR zaladowany bezposrednio")
            except Exception as e:
                print(f"[WARN] EasyOCR niedostepny: {str(e)[:50]}")
                self.use_easyocr = False
    
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
            
            # Preprocessing
            processed = self._preprocess(image)
            
            # Detekcja potencjalnych regionów tablic
            plate_candidates = self._detect_plate_regions(processed, image)
            
            if not plate_candidates:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono tablicy",
                    processing_time=time.time() - start_time
                )
            
            # Wybierz najlepszą kandydatkę
            best_candidate = max(plate_candidates, key=lambda x: x.get('area', 0))
            
            # Wycięcie regionu tablicy
            x1, y1, x2, y2 = best_candidate['bbox']
            plate_region = image[y1:y2, x1:x2]
            
            # OCR
            if self.ocr_engine:
                ocr_result = self.ocr_engine.recognize_plate(plate_region)
                plate_text = ocr_result.text
                confidence = ocr_result.confidence
            else:
                # Fallback: EasyOCR
                ocr_result = self._ocr_fallback(plate_region)
                plate_text = ocr_result.get('text', '')
                confidence = ocr_result.get('confidence', 0.0)
            
            processing_time = time.time() - start_time
            
            if not plate_text:
                return DetectionResult(
                    success=False,
                    error="Nie udało się odczytać tekstu z tablicy",
                    bbox=(x1, y1, x2, y2),
                    processing_time=processing_time
                )
            
            return DetectionResult(
                success=True,
                plate_text=plate_text,
                confidence=confidence,
                bbox=(x1, y1, x2, y2),
                processing_time=processing_time
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            return DetectionResult(
                success=False,
                error=f"Błąd: {str(e)[:50]}",
                processing_time=processing_time
            )
    
    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing obrazu"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Wyrównianie histogramu
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Rozmycie
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        return gray
    
    def _detect_plate_regions(self, gray: np.ndarray, original: np.ndarray) -> List[Dict]:
        """
        Detektuje potencjalne regiony tablic na podstawie konturów
        """
        # Detekcja krawędzi
        edges = cv2.Canny(gray, 100, 200)
        
        # Dylatacja
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edges = cv2.dilate(edges, kernel, iterations=2)
        
        # Kontur y
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 500:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # Sprawdzenie wymiarów
            if w < self.MIN_PLATE_WIDTH or h < self.MIN_PLATE_HEIGHT:
                continue
            if w > self.MAX_PLATE_WIDTH or h > self.MAX_PLATE_HEIGHT:
                continue
            
            # Aspect ratio
            aspect = w / h if h > 0 else 0
            if aspect < self.MIN_ASPECT_RATIO or aspect > self.MAX_ASPECT_RATIO:
                continue
            
            candidates.append({
                'bbox': (x, y, x + w, y + h),
                'area': area
            })
        
        return candidates
    
    def _ocr_fallback(self, plate_region: np.ndarray) -> Dict:
        """Fallback OCR przy użyciu EasyOCR"""
        try:
            if not self.use_easyocr or not self.reader:
                return {'text': '', 'confidence': 0.0}
            
            image_rgb = cv2.cvtColor(plate_region, cv2.COLOR_BGR2RGB)
            results = self.reader.readtext(image_rgb)
            
            if not results:
                return {'text': '', 'confidence': 0.0}
            
            texts = []
            confidences = []
            for (bbox, text, confidence) in results:
                clean = text.replace(' ', '').replace('-', '')
                if clean:
                    texts.append(clean)
                    confidences.append(confidence)
            
            if texts:
                combined_text = "".join(texts)[:8]
                avg_conf = np.mean(confidences) if confidences else 0.0
                return {'text': combined_text, 'confidence': float(avg_conf)}
            
            return {'text': '', 'confidence': 0.0}
        
        except Exception as e:
            return {'text': '', 'confidence': 0.0}
    
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
            if image_array is None or len(image_array.shape) < 2:
                return DetectionResult(
                    success=False,
                    error="Nieważny obraz",
                    processing_time=time.time() - start_time
                )
            
            # Preprocessing
            processed = self._preprocess(image_array)
            
            # Detekcja
            plate_candidates = self._detect_plate_regions(processed, image_array)
            
            if not plate_candidates:
                return DetectionResult(
                    success=False,
                    error="Nie znaleziono tablicy",
                    processing_time=time.time() - start_time
                )
            
            # Wybierz najlepszą
            best_candidate = max(plate_candidates, key=lambda x: x.get('area', 0))
            
            # Wycięcie
            x1, y1, x2, y2 = best_candidate['bbox']
            plate_region = image_array[y1:y2, x1:x2]
            
            # OCR
            if self.ocr_engine:
                ocr_result = self.ocr_engine.recognize_plate(plate_region)
                plate_text = ocr_result.text
                confidence = ocr_result.confidence
            else:
                ocr_result = self._ocr_fallback(plate_region)
                plate_text = ocr_result.get('text', '')
                confidence = ocr_result.get('confidence', 0.0)
            
            processing_time = time.time() - start_time
            
            if not plate_text:
                return DetectionResult(
                    success=False,
                    error="Nie udało się odczytać tablicy",
                    bbox=(x1, y1, x2, y2),
                    processing_time=processing_time
                )
            
            return DetectionResult(
                success=True,
                plate_text=plate_text,
                confidence=confidence,
                bbox=(x1, y1, x2, y2),
                processing_time=processing_time
            )
        
        except Exception as e:
            return DetectionResult(
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
