"""
Initializacja modułu backend
"""
from .queue_manager import get_queue, RedisQueue, RabbitMQQueue
from .database import get_db_session, save_result, get_all_results

__all__ = [
    'get_queue',
    'RedisQueue',
    'RabbitMQQueue',
    'get_db_session',
    'save_result',
    'get_all_results'
]
