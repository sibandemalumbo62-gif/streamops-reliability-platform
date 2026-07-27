import logging
from typing import Dict, Any
from uuid import UUID

from shared.kafka.producer import KafkaProducer
from shared.kafka.config import KafkaConfig, KafkaTopics, KafkaEventTypes

logger = logging.getLogger(__name__)


class PlaybackEventPublisher:
    """Publisher for playback-related events"""
    
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
    
    async def publish_playback_started(self, session_id: UUID, playback_data: Dict[str, Any]):
        """Publish playback started event"""
        await self.producer.publish_event(
            topic=KafkaTopics.PLAYBACK_EVENTS,
            event_type=KafkaEventTypes.PLAYBACK_STARTED,
            data={
                "session_id": str(session_id),
                "user_id": str(playback_data.get("user_id")),
                "content_id": str(playback_data.get("content_id")),
                "started_at": playback_data.get("started_at"),
                "device_type": playback_data.get("device_type")
            },
            key=str(playback_data.get("user_id"))
        )
    
    async def publish_playback_paused(self, session_id: UUID, position: int):
        """Publish playback paused event"""
        await self.producer.publish_event(
            topic=KafkaTopics.PLAYBACK_EVENTS,
            event_type=KafkaEventTypes.PLAYBACK_PAUSED,
            data={
                "session_id": str(session_id),
                "position": position
            },
            key=str(session_id)
        )
    
    async def publish_playback_resumed(self, session_id: UUID, position: int):
        """Publish playback resumed event"""
        await self.producer.publish_event(
            topic=KafkaTopics.PLAYBACK_EVENTS,
            event_type=KafkaEventTypes.PLAYBACK_RESUMED,
            data={
                "session_id": str(session_id),
                "position": position
            },
            key=str(session_id)
        )
    
    async def publish_playback_stopped(self, session_id: UUID, stop_data: Dict[str, Any]):
        """Publish playback stopped event"""
        await self.producer.publish_event(
            topic=KafkaTopics.PLAYBACK_EVENTS,
            event_type=KafkaEventTypes.PLAYBACK_STOPPED,
            data={
                "session_id": str(session_id),
                "user_id": str(stop_data.get("user_id")),
                "content_id": str(stop_data.get("content_id")),
                "watched_duration": stop_data.get("watched_duration"),
                "stopped_at": stop_data.get("stopped_at")
            },
            key=str(stop_data.get("user_id"))
        )
    
    async def publish_playback_completed(self, session_id: UUID, completion_data: Dict[str, Any]):
        """Publish playback completed event"""
        await self.producer.publish_event(
            topic=KafkaTopics.PLAYBACK_EVENTS,
            event_type=KafkaEventTypes.PLAYBACK_COMPLETED,
            data={
                "session_id": str(session_id),
                "user_id": str(completion_data.get("user_id")),
                "content_id": str(completion_data.get("content_id")),
                "completed_at": completion_data.get("completed_at")
            },
            key=str(completion_data.get("user_id"))
        )
