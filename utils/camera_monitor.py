"""
Moduł dla integracji z kamerą - Extended Scope
Umożliwia ciągły monitoring z kamery i real-time detekcję tablic
"""
import cv2
import time
import threading
from queue import Queue
from pathlib import Path
from datetime import datetime

from utils.plate_detector import PlateDetector
from backend.database import save_result


class CameraMonitor:
    """Monitor z kamerą dla detekcji tablic w real-time"""
    
    def __init__(self, camera_index: int = 0, detector: PlateDetector = None):
        """
        Inicjalizacja monitora
        
        Args:
            camera_index: Indeks kamery (0 dla wbudowanej)
            detector: Instancja detektora (jeśli None, będzie stworzona)
        """
        self.camera_index = camera_index
        self.detector = detector or PlateDetector()
        self.cap = None
        self.running = False
        self.frame_queue = Queue(maxsize=5)
        self.results_queue = Queue()
        self.fps = 0
        self.frame_count = 0
        self.start_time = None
    
    def open_camera(self) -> bool:
        """
        Otwiera kamerę
        
        Returns:
            bool: True jeśli sukces, False w przeciwnym razie
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                print(f"Błąd: Nie można otworzyć kamery {self.camera_index}")
                return False
            
            # Ustawienia kamery
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"✓ Kamera {self.camera_index} otwarta")
            return True
        
        except Exception as e:
            print(f"Błąd przy otwieraniu kamery: {e}")
            return False
    
    def close_camera(self):
        """Zamyka kamerę"""
        if self.cap:
            self.cap.release()
            print("Kamera zamknięta")
    
    def capture_frames(self):
        """Pętla przechwytywania ramek"""
        self.start_time = time.time()
        
        while self.running:
            ret, frame = self.cap.read()
            
            if not ret:
                print("Błąd przy czytaniu ramki")
                break
            
            self.frame_count += 1
            
            # Dodaj do kolejki (usuwając starą ramkę jeśli kolejka pełna)
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except:
                    pass
            
            self.frame_queue.put({
                'frame': frame,
                'timestamp': datetime.now()
            })
            
            # Oblicz FPS
            elapsed = time.time() - self.start_time
            self.fps = self.frame_count / elapsed if elapsed > 0 else 0
    
    def process_frames(self):
        """Pętla przetwarzania ramek"""
        while self.running:
            try:
                data = self.frame_queue.get(timeout=1)
                frame = data['frame']
                timestamp = data['timestamp']
                
                # Przeprowadź detekcję
                result = self.detector.detect_from_array(frame)
                
                if result.success:
                    # Zapisz wynik
                    save_result(
                        image_name=f"frame_{timestamp.isoformat()}",
                        predicted_plate=result.plate_text,
                        confidence=result.confidence,
                        processing_time=result.processing_time,
                        bbox=result.bbox,
                        success=True
                    )
                    
                    # Dodaj do wyników
                    self.results_queue.put({
                        'plate': result.plate_text,
                        'confidence': result.confidence,
                        'bbox': result.bbox,
                        'timestamp': timestamp
                    })
                    
                    print(f"[{timestamp.strftime('%H:%M:%S')}] "
                          f"Tablica: {result.plate_text} "
                          f"(pewność: {result.confidence:.2f})")
            
            except:
                pass
    
    def draw_detection_on_frame(self, frame, detection: dict) -> None:
        """
        Rysuje detektowaną tablicę na ramce
        
        Args:
            frame: Ramka OpenCV
            detection: Słownik z wynikami detekcji
        """
        if detection and 'bbox' in detection:
            x1, y1, x2, y2 = detection['bbox']
            
            # Rysuj bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Rysuj tekst
            text = f"{detection['plate']} ({detection['confidence']:.2f})"
            cv2.putText(frame, text, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    def display_frame(self, frame):
        """
        Wyświetla ramkę z informacjami
        
        Args:
            frame: Ramka do wyświetlenia
        """
        # Pokaż FPS
        fps_text = f"FPS: {self.fps:.1f}"
        cv2.putText(frame, fps_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Pokaż status
        status_text = "RECORDING - Press 'q' to quit"
        cv2.putText(frame, status_text, (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Pokaż ostatnią detektowaną tablicę
        try:
            last_result = self.results_queue.get_nowait()
            self.draw_detection_on_frame(frame, last_result)
        except:
            pass
        
        # Wyświetl
        cv2.imshow('License Plate Monitor', frame)
    
    def run(self):
        """Uruchomia monitoring"""
        print("=" * 60)
        print("LICENSE PLATE MONITOR - Extended Scope")
        print("=" * 60)
        print("Uruchamianie kamery...\n")
        
        if not self.open_camera():
            return
        
        self.running = True
        
        # Uruchom wątki
        capture_thread = threading.Thread(target=self.capture_frames, daemon=True)
        process_thread = threading.Thread(target=self.process_frames, daemon=True)
        
        capture_thread.start()
        process_thread.start()
        
        print("Monitor uruchomiony. Naciśnij 'q' aby zatrzymać.\n")
        
        try:
            while self.running:
                try:
                    data = self.frame_queue.get(timeout=1)
                    frame = data['frame']
                    
                    # Spróbuj pobrać ostatni wynik
                    try:
                        last_result = self.results_queue.get_nowait()
                        self.draw_detection_on_frame(frame, last_result)
                    except:
                        pass
                    
                    self.display_frame(frame)
                    
                    # Wciśnięcie 'q' zatrzymuje program
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                except KeyboardInterrupt:
                    break
                except:
                    pass
        
        finally:
            self.running = False
            self.close_camera()
            cv2.destroyAllWindows()
            print("\nMonitor zatrzymany.")
    
    def get_statistics(self) -> dict:
        """Zwraca statystyki monitoringu"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        return {
            'frames_captured': self.frame_count,
            'elapsed_time': elapsed,
            'avg_fps': self.fps,
            'results_in_queue': self.results_queue.qsize()
        }


def main():
    """Główna funkcja"""
    monitor = CameraMonitor(camera_index=0)
    monitor.run()


if __name__ == "__main__":
    main()
