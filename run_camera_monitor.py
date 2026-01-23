"""
Skrypt do uruchomienia monitora z kamerą (Extended Scope)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.camera_monitor import CameraMonitor

if __name__ == "__main__":
    print("Uruchamianie License Plate Monitor z kamerą...")
    print("(Extended Scope - Integracja z kamerą)")
    print("")
    
    monitor = CameraMonitor(camera_index=0)
    monitor.run()
