"""
Consumer - pracuje z kolejką i analizuje zdjęcia
"""
import time
import json
from pathlib import Path
import cv2
import numpy as np

from utils.config import config
from utils.plate_detector import PlateDetector
from backend.queue_manager import get_queue
from backend.database import save_result

ANALYSIS_QUEUE = "plate_analysis_queue"


class PlateAnalysisConsumer:
    """Consumer dla kolejki analiz tablic"""
    
    def __init__(self):
        self.queue = get_queue()
        self.detector = PlateDetector(languages=config.OCR_LANGUAGES)
        self.processed_count = 0
    
    def process_queue_item(self, queue_data: dict) -> bool:
        """
        Przetwarza pojedynczy element z kolejki
        
        Args:
            queue_data: Dane z kolejki
        
        Returns:
            bool: True jeśli sukces, False w przeciwnym razie
        """
        try:
            file_name = queue_data.get('file_name')
            file_content_hex = queue_data.get('file_content')
            
            # Konwertuj hex string z powrotem na bytes
            file_content = bytes.fromhex(file_content_hex)
            
            # Zdekoduj obraz
            nparr = np.frombuffer(file_content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                print(f"[CONSUMER] Błąd: Nie można wczytać obrazu {file_name}")
                return False
            
            # Przeprowadź detekcję i OCR
            result = self.detector.detect_from_array(img)
            
            # Zapisz wynik do bazy danych
            save_result(
                image_name=file_name,
                predicted_plate=result.plate_text or "",
                confidence=result.confidence,
                processing_time=result.processing_time,
                bbox=result.bbox,
                success=result.success
            )
            
            self.processed_count += 1
            
            status = "✓ SUKCES" if result.success else "✗ BŁĄD"
            print(f"[CONSUMER {self.processed_count}] {status}: {file_name} → {result.plate_text}")
            
            return True
        
        except Exception as e:
            print(f"[CONSUMER] Błąd przy przetwarzaniu: {str(e)}")
            return False
    
    def run(self, batch_size: int = 1, sleep_interval: float = 0.5):
        """
        Uruchomia consumer - ciągle czeka na elementy w kolejce
        
        Args:
            batch_size: Ile elementów przetwarzać naraz
            sleep_interval: Czas oczekiwania między sprawdzeniami kolejki (sekundy)
        """
        print(f"[CONSUMER] Startowanie consumera dla kolejki: {ANALYSIS_QUEUE}")
        print(f"[CONSUMER] Queue system: {config.QUEUE_SYSTEM}")
        
        try:
            while True:
                # Pobierz elementy z kolejki
                processed_this_iteration = 0
                
                for i in range(batch_size):
                    queue_data = self.queue.pop(ANALYSIS_QUEUE)
                    
                    if queue_data is None:
                        break
                    
                    self.process_queue_item(queue_data)
                    processed_this_iteration += 1
                
                if processed_this_iteration == 0:
                    # Brak danych w kolejce, poczekaj
                    time.sleep(sleep_interval)
                
        except KeyboardInterrupt:
            print("\n[CONSUMER] Zatrzymywanie consumera...")
        except Exception as e:
            print(f"[CONSUMER] Błąd: {str(e)}")


def main():
    """Główna funkcja"""
    consumer = PlateAnalysisConsumer()
    consumer.run(batch_size=5, sleep_interval=1.0)


if __name__ == "__main__":
    main()
