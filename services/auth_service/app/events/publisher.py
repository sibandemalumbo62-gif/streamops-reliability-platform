import logging
from typing import Dict, Any
from uuid import UUID

from shared.kafka.producer import KafkaProducer
from shared.kafka.config import KafkaConfig, KafkaTopics, KafkaEventTypes

logger = logging.getLogger(__name__)


class AuthEventPublisher:
    """Publisher for authentication-related events"""
    
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
    
    async def publish_user_created(self, user_id: UUID, user_data: Dict[str, Any]):
        """Publish user created event"""
        await self.producer.publish_event(
            topic=KafkaTopics.USER_EVENTS,
            event_type=KafkaEventTypes.USER_CREATED,
            data={
                "user_id": str(user_id),
                "email": user_data.get("email"),
                "username": user_data.get("username"),
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name")
            },
            key=str(user_id)
        )
    
    async def publish_user_updated(self, user_id: UUID, updated_fields: Dict[str, Any]):
        """Publish user updated event"""
        await self.producer.publish_event(
            topic=KafkaTopics.USER_EVENTS,
            event_type=KafkaEventTypes.USER_UPDATED,
            data={
                "user_id": str(user_id),
                "updated_fields": updated_fields
            },
            key=str(user_id)
        )
    
    async def publish_user_login(self, user_id: UUID, login_data: Dict[str, Any]):
        """Publish user login event"""
        await self.producer.publish_event(
            topic=KafkaTopics.USER_EVENTS,
            event_type=KafkaEventTypes.USER_LOGIN,
            data={
                "user_id": str(user_id),
                "timestamp": login_data.get("timestamp"),
                "ip_address": login_data.get("ip_address"),
                "user_agent": login_data.get("user_agent")
            },
            key=str(user_id)
        )
    
    async def publish_user_logout(self, user_id: UUID):
        """Publish user logout event"""
        await self.producer.publish_event(
            topic=KafkaTopics.USER_EVENTS,
            event_type=KafkaEventTypes.USER_LOGOUT,
            data={
                "user_id": str(user_id)
            },
            key=str(user_id)
        )
