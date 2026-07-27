import json
import logging
from typing import Callable, Dict, Any
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Async Kafka consumer for event processing"""
    
    def __init__(self, bootstrap_servers: str, group_id: str):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = None
        self.handlers: Dict[str, Callable] = {}
    
    async def start(self, topics: list[str]):
        """Initialize the Kafka consumer and subscribe to topics"""
        try:
            self.consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            await self.consumer.start()
            logger.info(f"Kafka consumer connected to {self.bootstrap_servers}, subscribed to {topics}")
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise
    
    async def stop(self):
        """Stop the Kafka consumer"""
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
    
    def register_handler(self, event_type: str, handler: Callable):
        """
        Register a handler for a specific event type
        
        Args:
            event_type: Event type to handle (e.g., 'user.created')
            handler: Async function to handle the event
        """
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")
    
    async def consume_events(self):
        """Start consuming and processing events"""
        if not self.consumer:
            logger.error("Kafka consumer not initialized")
            return
        
        try:
            async for msg in self.consumer:
                try:
                    event = msg.value
                    event_type = event.get('event_type')
                    
                    if event_type in self.handlers:
                        handler = self.handlers[event_type]
                        await handler(event)
                        logger.info(f"Processed event {event_type} from topic {msg.topic}")
                    else:
                        logger.warning(f"No handler registered for event type: {event_type}")
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except KafkaError as e:
            logger.error(f"Kafka error consuming events: {e}")
        except Exception as e:
            logger.error(f"Unexpected error consuming events: {e}")
