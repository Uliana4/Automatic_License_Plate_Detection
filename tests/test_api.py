"""
Skrypt do testowania endpoints API
"""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"


def test_root():
    """Test endpoint głównego"""
    print("Testing GET /")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_analyze(image_path: str):
    """Test endpoint analizy"""
    print(f"Testing POST /analyze with {Path(image_path).name}")
    
    with open(image_path, 'rb') as f:
        files = {'file': (Path(image_path).name, f)}
        response = requests.post(f"{BASE_URL}/analyze", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_queue_analysis(image_path: str):
    """Test endpoint dodania do kolejki"""
    print(f"Testing POST /queue-analysis with {Path(image_path).name}")
    
    with open(image_path, 'rb') as f:
        files = {'file': (Path(image_path).name, f)}
        response = requests.post(f"{BASE_URL}/queue-analysis", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_queue_status():
    """Test status kolejki"""
    print("Testing GET /queue-status")
    response = requests.get(f"{BASE_URL}/queue-status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_clear_queue():
    """Test czyszczenia kolejki"""
    print("Testing POST /clear-queue")
    response = requests.post(f"{BASE_URL}/clear-queue")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def main():
    """Testuj wszystkie endpoints"""
    print("=" * 60)
    print("TESTOWANIE API ENDPOINTS")
    print("=" * 60 + "\n")
    
    # Sprawdzenie dostępu do API
    try:
        test_root()
    except requests.exceptions.ConnectionError:
        print("Błąd: Nie można połączyć się z API")
        print("Upewnij się, że backend jest uruchomiony: python -m backend.main")
        return
    
    # Znajdź przykładowe zdjęcie
    photos_dir = Path(__file__).parent.parent / "photos"
    if photos_dir.exists():
        image_files = list(photos_dir.glob("*.jpg"))[:1]
        
        if image_files:
            test_image = str(image_files[0])
            
            # Test analizy
            test_analyze(test_image)
            
            # Test kolejki
            test_queue_analysis(test_image)
            test_queue_status()
            test_clear_queue()
    else:
        print(f"Nie znaleziono folderu z zdjęciami: {photos_dir}")


if __name__ == "__main__":
    main()
