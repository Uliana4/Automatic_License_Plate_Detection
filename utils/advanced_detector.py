"""
Rozszerzone modele detekcji - opcjonalne YOLO dla lepszej wydajności
"""
import cv2
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class YOLODetectionResult:
    """Rezultat detekcji YOLO"""
    success: bool
    boxes: list = None  # Lista bounding boxów
    confidence: list = None
    processing_time: float = 0.0
    error: Optional[str] = None


class YOLOPlateDetector:
    """
    Detektor tablic z użyciem YOLO (opcjonalnie)
    
    Do użycia: 
    1. Pobrać weights z https://github.com/WongKinYiu/YOLOv7
    2. Ewentualnie przeszkolić na zbiorze tablic
    """
    
    def __init__(self, weights_path: str = None):
        """
        Inicjalizacja YOLO
        
        Args:
            weights_path: Ścieżka do wag YOLO
        """
        try:
            import torch
            from ultralytics import YOLO
            
            if weights_path is None:
                # Używaj pre-trained YOLOv8
                self.model = YOLO('yolov8n.pt')
            else:
                self.model = YOLO(weights_path)
                
            self.available = True
        except ImportError:
            print("YOLO niedostępny. Aby używać YOLO: pip install ultralytics torch")
            self.available = False
    
    def detect_plates(self, image_path: str) -> YOLODetectionResult:
        """
        Detektuje tablice za pomocą YOLO
        """
        if not self.available:
            return YOLODetectionResult(
                success=False,
                error="YOLO niedostępny"
            )
        
        try:
            results = self.model.predict(image_path, conf=0.5)
            
            boxes = []
            confidences = []
            
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = box.conf[0].item()
                    boxes.append((int(x1), int(y1), int(x2), int(y2)))
                    confidences.append(conf)
            
            return YOLODetectionResult(
                success=True,
                boxes=boxes,
                confidence=confidences
            )
        
        except Exception as e:
            return YOLODetectionResult(
                success=False,
                error=str(e)
            )


# Metody preprocessing dla lepszej wydajności
def preprocess_image(image_path: str, max_size: int = 1920) -> np.ndarray:
    """
    Preprocessing obrazu
    
    Args:
        image_path: Ścieżka do obrazu
        max_size: Maksymalny rozmiar (dla szybkości)
    
    Returns:
        Przetworzony obraz
    """
    img = cv2.imread(image_path)
    
    # Resize jeśli za duży
    height, width = img.shape[:2]
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = cv2.resize(img, (new_width, new_height))
    
    # CLAHE - zwiększenie kontrastu
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    return img


def enhance_plate_region(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Poprawia region tablicy dla lepszego OCR
    
    Args:
        image: Obraz
        bbox: Bounding box tablicy (x1, y1, x2, y2)
    
    Returns:
        Powiększony i wzmocniony region
    """
    x1, y1, x2, y2 = bbox
    plate = image[y1:y2, x1:x2]
    
    # Wzmocnienie kontrastu
    lab = cv2.cvtColor(plate, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    plate = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # Thresholding dla lepszego OCR
    gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    _, plate = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Powiększenie
    scale = 2
    plate = cv2.resize(plate, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    return plate
