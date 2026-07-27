import logging
from typing import Dict, Any
from uuid import UUID

from shared.kafka.producer import KafkaProducer
from shared.kafka.config import KafkaConfig, KafkaTopics, KafkaEventTypes

logger = logging.getLogger(__name__)


class NotificationEventPublisher:
    """Publisher for notification-related events"""
    
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
    
    async def publish_notification_sent(self, notification_id: UUID, notification_data: Dict[str, Any]):
        """Publish notification sent event"""
        await self.producer.publish_event(
            topic=KafkaTopics.NOTIFICATION_EVENTS,
            event_type=KafkaEventTypes.NOTIFICATION_SENT,
            data={
                "notification_id": str(notification_id),
                "user_id": str(notification_data.get("user_id")),
                "type": notification_data.get("type"),
                "channel": notification_data.get("channel"),
                "sent_at": notification_data.get("sent_at")
            },
            key=str(notification_data.get("user_id"))
        )
    
    async def publish_notification_read(self, notification_id: UUID, user_id: UUID):
        """Publish notification read event"""
        await self.producer.publish_event(
            topic=KafkaTopics.NOTIFICATION_EVENTS,
            event_type=KafkaEventTypes.NOTIFICATION_READ,
            data={
                "notification_id": str(notification_id),
                "user_id": str(user_id)
            },
            key=str(user_id)
        )
