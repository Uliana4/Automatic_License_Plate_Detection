"""
OCR Engine - wielopoziomowa implementacja OCR dla rozpoznawania tablic
Wspiera: EasyOCR (A), Tesseract (B) - z oficjalnej listy rekomendacji
Opcjonalnie: PaddleOCR (C) - jeśli zainstalowany
"""
import cv2
import numpy as np
import time
import string
import re
import threading
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class OCRResult:
    """Wynik OCR"""
    text: str
    confidence: float
    method: str  # 'easyocr', 'tesseract', 'paddle' (opcjonalnie)


class OCREngine:
    """
    Wielopoziomowy silnik OCR z fallbackami
    Używa oficjalnie rekomendowanych metod:
    A. EasyOCR - szybka, dokładna
    B. Tesseract - lightweight fallback
    C. PaddleOCR - opcjonalnie, jeśli zainstalowany
    """
    
    # Polskie znaki tablicowe
    VALID_PLATE_CHARS = set(string.ascii_uppercase + "0123456789 ")
    POLISH_REGIONS = [
        "SCZ", "SK", "STA", "SZA", "SJ", "SH", "WA", "WG", "WZ", "WI",
        "WA", "WB", "WD", "WE", "WF", "WG", "WH", "WI", "WJ", "WK",
        "WL", "WM", "WN", "WO", "WP", "WR", "WS", "WT", "WU", "WW",
        "ZA", "ZI", "ZS", "ZSL"
    ]
    
    def __init__(self):
        """Inicjalizacja OCR Engine"""
        self.easyocr_reader = None
        self.easyocr_available = False
        self.tesseract_available = False
        self.paddle_available = False
        self.paddle_ocr = None
        
        # Spróbuj załadować EasyOCR (OPCJA A - PODSTAWOWA)
        try:
            import easyocr
            self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
            self.easyocr_available = True
            print("[OK] EasyOCR dostepny (A - rekomendacja)")
        except Exception as e:
            print(f"[WARN] EasyOCR niedostepny: {str(e)[:50]}")
        
        # Spróbuj załadować Tesseract (OPCJA B - FALLBACK)
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
            print("[OK] Tesseract dostepny (B - rekomendacja)")
        except Exception as e:
            print(f"[WARN] Tesseract niedostepny: {str(e)[:50]}")
        
        # Opcjonalnie: Spróbuj załadować PaddleOCR (OPCJA C - BONUS)
        try:
            from paddleocr import PaddleOCR
            self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
            self.paddle_available = True
            print("[OK] PaddleOCR dostepny (C - opcjonalnie)")
        except Exception:
            # Cicho ignoruj - to opcjonalne
            pass
    
    
    def recognize_plate(self, image: np.ndarray, plate_region: Optional[np.ndarray] = None) -> OCRResult:
        """
        Rozpoznaj tablicę rejestracyjną
        
        Próbuje kolejno (z listy rekomendacji):
        A. EasyOCR - szybka, dokładna (GŁÓWNA)
        B. Tesseract - lightweight fallback
        C. PaddleOCR - opcjonalnie, jeśli zainstalowany
        
        Args:
            image: Obraz wejściowy (BGR)
            plate_region: Opcjonalnie: wycięty region tablicy
        
        Returns:
            OCRResult: Tekst + confidence + metoda
        """
        if plate_region is None:
            plate_region = image
        
        # Normalny rozmiar dla OCR: min 150px szerokości
        if plate_region.shape[1] < 150:
            plate_region = cv2.resize(plate_region, None, fx=2, fy=2)
        
        # Spróbuj EasyOCR (OPCJA A - GŁÓWNA)
        if self.easyocr_available:
            result = self._ocr_easyocr(plate_region)
            if result is not None:
                return result
        
        # Spróbuj Tesseract (OPCJA B - FALLBACK)
        if self.tesseract_available:
            result = self._ocr_tesseract(plate_region)
            if result is not None:
                return result
        
        # Opcjonalnie spróbuj PaddleOCR (OPCJA C - BONUS)
        if self.paddle_available:
            result = self._ocr_paddle(plate_region)
            if result is not None:
                return result
        
        # Fallback
        return OCRResult("", 0.0, "no-ocr")
    
    def _ocr_easyocr(self, image: np.ndarray) -> Optional[OCRResult]:
        """EasyOCR - bez timeoutu na Windows"""
        try:
            if not self.easyocr_available or not self.easyocr_reader:
                return None
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.easyocr_reader.readtext(image_rgb)
            
            if not results:
                return None
            
            texts = []
            confidences = []
            for (bbox, text, confidence) in results:
                clean_text = self._clean_plate_text(text)
                if clean_text:
                    texts.append(clean_text)
                    confidences.append(confidence)
            
            if texts:
                plate_text = "".join(texts[:8])
                avg_conf = np.mean(confidences) if confidences else 0.0
                return OCRResult(plate_text, avg_conf, "easyocr")
            
            return None
        
        except Exception as e:
            print(f"[ERROR] EasyOCR: {str(e)[:40]}")
            return None
    
    def _ocr_paddle(self, image: np.ndarray) -> Optional[OCRResult]:
        """PaddleOCR - z oficjalnej listy rekomendacji (OPCJA C)"""
        try:
            if not self.paddle_available or not self.paddle_ocr:
                return None
            
            # PaddleOCR pracuje bezpośrednio na BGR
            results = self.paddle_ocr.ocr(image, cls=True)
            
            if not results or not results[0]:
                return None
            
            texts = []
            confidences = []
            
            for line in results[0]:
                if line and len(line) >= 2:
                    text = line[1][0]  # Tekst
                    confidence = line[1][1]  # Confidence
                    
                    clean_text = self._clean_plate_text(text)
                    if clean_text:
                        texts.append(clean_text)
                        confidences.append(confidence)
            
            if texts:
                plate_text = "".join(texts[:8])
                avg_conf = np.mean(confidences) if confidences else 0.0
                return OCRResult(plate_text, avg_conf, "paddle")
            
            return None
        
        except Exception as e:
            print(f"[ERROR] PaddleOCR: {str(e)[:40]}")
            return None
    
    def _ocr_tesseract(self, image: np.ndarray) -> Optional[OCRResult]:
        """Tesseract - z oficjalnej listy rekomendacji (OPCJA B)"""
        try:
            import pytesseract
            
            # Preprocessing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Thresholding
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR
            text = pytesseract.image_to_string(
                binary,
                config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            ).strip()
            
            if text:
                clean_text = self._clean_plate_text(text)
                if clean_text:
                    return OCRResult(clean_text, 0.85, "tesseract")
            
            return None
        
        except Exception as e:
            print(f"[ERROR] Tesseract: {str(e)[:40]}")
            return None
    
    def _clean_plate_text(self, text: str) -> str:
        """
        Oczyszcza tekst OCR do formatu tablicy rejestracyjnej
        
        Format polski: DDD99999 (3 litery + 5 cyfr) lub DD9999 (2 litery + 4 cyfry)
        """
        # Usuń białe znaki
        text = text.replace(" ", "").upper()
        
        # Usuń znaki spoza zakresu
        text = "".join([c for c in text if c in self.VALID_PLATE_CHARS])
        
        # Ekstrakcja: wzór tablicy - szukaj 2-3 liter na początku
        match = re.match(r'^([A-Z]{2,3})(\d{4,5})(.*)$', text)
        if match:
            letters = match.group(1)
            numbers = match.group(2)
            region = match.group(3)[:2] if match.group(3) else ""
            
            plate = f"{letters}{numbers}{region}"
            if len(plate) >= 7:
                return plate[:8]
        
        # Alternatywnie: szukaj bloków liter i cyfr
        letters = "".join([c for c in text if c.isalpha()][:3])
        numbers = "".join([c for c in text if c.isdigit()][:5])
        
        if len(letters) >= 2 and len(numbers) >= 4:
            return f"{letters}{numbers}"
        
        return ""
    
    def validate_plate(self, plate_text: str) -> bool:
        """
        Sprawdza czy tekst wygląda jak polska tablica rejestracyjna
        """
        if not plate_text or len(plate_text) < 7:
            return False
        
        match = re.match(r'^([A-Z]{2,3})(\d{4,5})(.*)$', plate_text)
        return match is not None
