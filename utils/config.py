"""
Konfiguracja aplikacji
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = 0
    
    # RabbitMQ
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./database.db')
    
    # Queue system
    QUEUE_SYSTEM = os.getenv('QUEUE_SYSTEM', 'redis')  # redis or rabbitmq
    
    # Paths
    PHOTOS_DIR = os.path.join(os.path.dirname(__file__), '..', 'photos')
    ANNOTATIONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'annotations.xml')
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
    MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
    
    # OCR Settings
    OCR_LANGUAGES = ['en']  # Język dla OCR - dla polskich tablic
    DETECTION_CONFIDENCE = 0.5
    
    # Processing
    MAX_IMAGE_SIZE = 1920
    BATCH_SIZE = 32


config = Config()
