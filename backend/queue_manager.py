"""
Moduł obsługi kolejek - abstrakacja dla Redis i RabbitMQ
"""
import json
import redis
import pika
from abc import ABC, abstractmethod
from typing import Dict, Optional
from utils.config import config


class QueueBase(ABC):
    """Abstrakcyjna klasa dla systemu kolejek"""
    
    @abstractmethod
    def push(self, queue_name: str, data: Dict) -> bool:
        """Dodaj wiadomość do kolejki"""
        pass
    
    @abstractmethod
    def pop(self, queue_name: str) -> Optional[Dict]:
        """Pobierz wiadomość z kolejki"""
        pass
    
    @abstractmethod
    def get_queue_size(self, queue_name: str) -> int:
        """Pobierz rozmiar kolejki"""
        pass
    
    @abstractmethod
    def clear(self, queue_name: str) -> bool:
        """Wyczyść kolejkę"""
        pass


class RedisQueue(QueueBase):
    """Implementacja kolejki na Redis"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True
        )
    
    def push(self, queue_name: str, data: Dict) -> bool:
        """Dodaj wiadomość do kolejki"""
        try:
            json_data = json.dumps(data)
            self.redis_client.rpush(queue_name, json_data)
            return True
        except Exception as e:
            print(f"Błąd przy dodawaniu do kolejki Redis: {e}")
            return False
    
    def pop(self, queue_name: str) -> Optional[Dict]:
        """Pobierz wiadomość z kolejki"""
        try:
            json_data = self.redis_client.lpop(queue_name)
            if json_data:
                return json.loads(json_data)
            return None
        except Exception as e:
            print(f"Błąd przy pobieraniu z kolejki Redis: {e}")
            return None
    
    def get_queue_size(self, queue_name: str) -> int:
        """Pobierz rozmiar kolejki"""
        try:
            return self.redis_client.llen(queue_name)
        except Exception as e:
            print(f"Błąd przy pobieraniu rozmiaru kolejki: {e}")
            return 0
    
    def clear(self, queue_name: str) -> bool:
        """Wyczyść kolejkę"""
        try:
            self.redis_client.delete(queue_name)
            return True
        except Exception as e:
            print(f"Błąd przy czyszczeniu kolejki: {e}")
            return False


class RabbitMQQueue(QueueBase):
    """Implementacja kolejki na RabbitMQ"""
    
    def __init__(self):
        credentials = pika.PlainCredentials(
            config.RABBITMQ_USER,
            config.RABBITMQ_PASSWORD
        )
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                port=config.RABBITMQ_PORT,
                credentials=credentials
            )
        )
        self.channel = self.connection.channel()
    
    def push(self, queue_name: str, data: Dict) -> bool:
        """Dodaj wiadomość do kolejki"""
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            json_data = json.dumps(data)
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json_data,
                properties=pika.BasicProperties(
                    delivery_mode=2  # persistent
                )
            )
            return True
        except Exception as e:
            print(f"Błąd przy dodawaniu do kolejki RabbitMQ: {e}")
            return False
    
    def pop(self, queue_name: str) -> Optional[Dict]:
        """Pobierz wiadomość z kolejki"""
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            method, properties, body = self.channel.basic_get(queue_name)
            if method:
                self.channel.basic_ack(delivery_tag=method.delivery_tag)
                return json.loads(body.decode('utf-8'))
            return None
        except Exception as e:
            print(f"Błąd przy pobieraniu z kolejki RabbitMQ: {e}")
            return None
    
    def get_queue_size(self, queue_name: str) -> int:
        """Pobierz rozmiar kolejki"""
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            method = self.channel.queue_declare(
                queue=queue_name,
                passive=True
            )
            return method.method.message_count
        except Exception as e:
            print(f"Błąd przy pobieraniu rozmiaru kolejki: {e}")
            return 0
    
    def clear(self, queue_name: str) -> bool:
        """Wyczyść kolejkę"""
        try:
            self.channel.queue_purge(queue=queue_name)
            return True
        except Exception as e:
            print(f"Błąd przy czyszczeniu kolejki: {e}")
            return False


def get_queue() -> QueueBase:
    """Zwraca instancję odpowiedniego systemu kolejek"""
    if config.QUEUE_SYSTEM == 'rabbitmq':
        return RabbitMQQueue()
    else:
        return RedisQueue()
