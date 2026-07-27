import logging
from typing import Dict, Any
from uuid import UUID

from shared.kafka.producer import KafkaProducer
from shared.kafka.config import KafkaConfig, KafkaTopics, KafkaEventTypes

logger = logging.getLogger(__name__)


class CatalogEventPublisher:
    """Publisher for catalog/content-related events"""
    
    def __init__(self):
        self.producer = None
        self.bootstrap_servers = KafkaConfig.get_bootstrap_servers()
    
    async def initialize(self):
        """Initialize the Kafka producer"""
        self.producer = KafkaProducer(self.bootstrap_servers)
        await self.producer.start()
    
    async def shutdown(self):
        """Shutdown the Kafka producer"""
        if self.producer:
            await self.producer.stop()
    
    async def publish_content_created(self, content_id: UUID, content_data: Dict[str, Any]):
        """Publish content created event"""
        await self.producer.publish_event(
            topic=KafkaTopics.CONTENT_EVENTS,
            event_type=KafkaEventTypes.CONTENT_CREATED,
            data={
                "content_id": str(content_id),
                "title": content_data.get("title"),
                "content_type": content_data.get("content_type"),
                "genre": content_data.get("genre"),
                "duration": content_data.get("duration"),
                "release_date": content_data.get("release_date")
            },
            key=str(content_id)
        )
    
    async def publish_content_updated(self, content_id: UUID, updated_fields: Dict[str, Any]):
        """Publish content updated event"""
        await self.producer.publish_event(
            topic=KafkaTopics.CONTENT_EVENTS,
            event_type=KafkaEventTypes.CONTENT_UPDATED,
            data={
                "content_id": str(content_id),
                "updated_fields": updated_fields
            },
            key=str(content_id)
        )
    
    async def publish_content_deleted(self, content_id: UUID):
        """Publish content deleted event"""
        await self.producer.publish_event(
            topic=KafkaTopics.CONTENT_EVENTS,
            event_type=KafkaEventTypes.CONTENT_DELETED,
            data={
                "content_id": str(content_id)
            },
            key=str(content_id)
        )
    
    async def publish_content_published(self, content_id: UUID, publish_data: Dict[str, Any]):
        """Publish content published event"""
        await self.producer.publish_event(
            topic=KafkaTopics.CONTENT_EVENTS,
            event_type=KafkaEventTypes.CONTENT_PUBLISHED,
            data={
                "content_id": str(content_id),
                "published_at": publish_data.get("published_at"),
                "availability": publish_data.get("availability")
            },
            key=str(content_id)
        )
