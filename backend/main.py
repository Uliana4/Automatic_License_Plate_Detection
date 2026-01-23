"""
FastAPI Backend - Endpoints dla aplikacji
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from io import BytesIO
import os

from utils.config import config
from utils.plate_detector import PlateDetector
from backend.queue_manager import get_queue
from backend.database import save_result

# Inicjalizacja FastAPI
app = FastAPI(title="License Plate Recognition API")

# Inicjalizacja detektora
detector = PlateDetector(languages=config.OCR_LANGUAGES)
queue = get_queue()

# Queue names
ANALYSIS_QUEUE = "plate_analysis_queue"


@app.get("/")
async def root():
    """Endpoint główny"""
    return {"message": "License Plate Recognition API"}


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Endpoint do natychmiastowej analizy przesłanego zdjęcia
    
    Returns:
        - success: bool
        - plate_text: str (numer tablicy)
        - confidence: float
        - bbox: tuple (xtl, ytl, xbr, ybr)
        - processing_time: float
    """
    try:
        # Wczytaj obraz z przesłanego pliku
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Nie można wczytać obrazu")
        
        # Przeprowadź detekcję i OCR
        result = detector.detect_from_array(img)
        
        # Zapisz wynik do bazy danych
        save_result(
            image_name=file.filename,
            predicted_plate=result.plate_text or "",
            confidence=result.confidence,
            processing_time=result.processing_time,
            bbox=result.bbox,
            success=result.success
        )
        
        return JSONResponse({
            "success": result.success,
            "plate_text": result.plate_text,
            "confidence": float(result.confidence),
            "bbox": result.bbox,
            "processing_time": result.processing_time,
            "error": result.error
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.post("/queue-analysis")
async def queue_analysis(file: UploadFile = File(...)):
    """
    Endpoint do dodania zdjęcia do kolejki do asynchronicznej analizy
    
    Returns:
        - success: bool
        - queue_size: int (rozmiar kolejki)
        - file_name: str
    """
    try:
        # Odczytaj zawartość pliku
        contents = await file.read()
        
        # Przygotuj dane dla kolejki
        queue_data = {
            "file_name": file.filename,
            "file_content": contents.hex(),  # Konwertuj bytes na hex string
            "content_type": file.content_type
        }
        
        # Dodaj do kolejki
        success = queue.push(ANALYSIS_QUEUE, queue_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Błąd przy dodaniu do kolejki")
        
        queue_size = queue.get_queue_size(ANALYSIS_QUEUE)
        
        return JSONResponse({
            "success": True,
            "message": "Zdjęcie dodane do kolejki",
            "queue_size": queue_size,
            "file_name": file.filename
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.get("/queue-status")
async def queue_status():
    """Sprawdz status kolejki"""
    try:
        queue_size = queue.get_queue_size(ANALYSIS_QUEUE)
        
        return JSONResponse({
            "queue_size": queue_size,
            "queue_system": config.QUEUE_SYSTEM
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.post("/clear-queue")
async def clear_queue():
    """Wyczyść kolejkę"""
    try:
        success = queue.clear(ANALYSIS_QUEUE)
        
        return JSONResponse({
            "success": success,
            "message": "Kolejka wyczyszczona" if success else "Błąd czyszczenia kolejki"
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
