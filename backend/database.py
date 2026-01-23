"""
Moduł bazy danych dla przechowywania wyników
"""
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from utils.config import config

Base = declarative_base()


class PlateResult(Base):
    """Model przechowywania wyników OCR"""
    __tablename__ = "plate_results"
    
    id = Column(Integer, primary_key=True, index=True)
    image_name = Column(String, index=True)
    predicted_plate = Column(String)
    ground_truth_plate = Column(String, nullable=True)
    confidence = Column(Float)
    processing_time = Column(Float)
    bbox_xtl = Column(Float)
    bbox_ytl = Column(Float)
    bbox_xbr = Column(Float)
    bbox_ybr = Column(Float)
    success = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


# Inicjalizacja bazy danych
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Zwraca sesję bazy danych"""
    return SessionLocal()


def save_result(image_name: str, predicted_plate: str, confidence: float,
                processing_time: float, bbox, success: bool,
                ground_truth_plate: str = None) -> bool:
    """
    Zapisuje wynik do bazy danych
    
    Returns:
        bool: True jeśli sukces, False w przeciwnym razie
    """
    try:
        session = get_db_session()
        
        result = PlateResult(
            image_name=image_name,
            predicted_plate=predicted_plate,
            ground_truth_plate=ground_truth_plate,
            confidence=confidence,
            processing_time=processing_time,
            bbox_xtl=bbox[0] if bbox else 0,
            bbox_ytl=bbox[1] if bbox else 0,
            bbox_xbr=bbox[2] if bbox else 0,
            bbox_ybr=bbox[3] if bbox else 0,
            success="success" if success else "failed"
        )
        
        session.add(result)
        session.commit()
        session.close()
        return True
    except Exception as e:
        print(f"Błąd przy zapisie do bazy danych: {e}")
        return False


def get_all_results():
    """Pobiera wszystkie wyniki"""
    try:
        session = get_db_session()
        results = session.query(PlateResult).all()
        session.close()
        return results
    except Exception as e:
        print(f"Błąd przy pobieraniu wyników: {e}")
        return []
