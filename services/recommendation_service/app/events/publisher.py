import logging
from typing import Dict, Any
from uuid import UUID

from shared.kafka.producer import KafkaProducer
from shared.kafka.config import KafkaConfig, KafkaTopics, KafkaEventTypes

logger = logging.getLogger(__name__)


class RecommendationEventPublisher:
    """Publisher for recommendation-related events"""
    
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
    
    async def publish_recommendation_generated(self, user_id: UUID, recommendation_data: Dict[str, Any]):
        """Publish recommendation generated event"""
        await self.producer.publish_event(
            topic=KafkaTopics.RECOMMENDATION_EVENTS,
            event_type=KafkaEventTypes.RECOMMENDATION_GENERATED,
            data={
                "user_id": str(user_id),
                "recommendations": recommendation_data.get("recommendations", []),
                "algorithm": recommendation_data.get("algorithm"),
                "generated_at": recommendation_data.get("generated_at")
            },
            key=str(user_id)
        )
    
    async def publish_preference_updated(self, user_id: UUID, preference_data: Dict[str, Any]):
        """Publish preference updated event"""
        await self.producer.publish_event(
            topic=KafkaTopics.RECOMMENDATION_EVENTS,
            event_type=KafkaEventTypes.PREFERENCE_UPDATED,
            data={
                "user_id": str(user_id),
                "preferences": preference_data.get("preferences", {}),
                "updated_at": preference_data.get("updated_at")
            },
            key=str(user_id)
        )
