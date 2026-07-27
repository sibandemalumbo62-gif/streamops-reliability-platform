import json
import logging
from typing import Any, Dict

try:
    from aiokafka import AIOKafkaProducer  # type: ignore[import]
except ImportError:
    AIOKafkaProducer = None

try:
    from kafka.errors import KafkaError  # type: ignore[import]
except ImportError:
    KafkaError = Exception

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Async Kafka producer for event publishing"""
    
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
    
    async def start(self):
        """Initialize the Kafka producer"""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            await self.producer.start()
            logger.info(f"Kafka producer connected to {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise
    
    async def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def publish_event(
        self,
        topic: str,
        event_type: str,
        data: Dict[str, Any],
        key: str = None,
        headers: Dict[str, str] = None
    ) -> bool:
        """
        Publish an event to a Kafka topic
        
        Args:
            topic: Kafka topic name
            event_type: Type of event (e.g., 'user.created', 'playback.started')
            data: Event payload
            key: Optional partition key
            headers: Optional event headers
            
        Returns:
            True if published successfully, False otherwise
        """
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            event = {
                "event_type": event_type,
                "timestamp": self._get_timestamp(),
                "data": data
            }
            
            # Add headers if provided
            kafka_headers = []
            if headers:
                for k, v in headers.items():
                    kafka_headers.append((k, v.encode('utf-8')))
            
            await self.producer.send_and_wait(
                topic,
                value=event,
                key=key,
                headers=kafka_headers if kafka_headers else None
            )
            
            logger.info(f"Event {event_type} published to {topic}")
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error publishing event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}")
            return False
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
