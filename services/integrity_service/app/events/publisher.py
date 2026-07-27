import logging
from typing import Dict, Any
from uuid import UUID

from shared.kafka.producer import KafkaProducer
from shared.kafka.config import KafkaConfig, KafkaTopics, KafkaEventTypes

logger = logging.getLogger(__name__)


class IntegrityEventPublisher:
    """Publisher for integrity-related events"""
    
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
    
    async def publish_event_validated(self, event_id: UUID, validation_data: Dict[str, Any]):
        """Publish event validated event"""
        await self.producer.publish_event(
            topic=KafkaTopics.INTEGRITY_EVENTS,
            event_type=KafkaEventTypes.EVENT_VALIDATED,
            data={
                "event_id": str(event_id),
                "is_valid": validation_data.get("is_valid"),
                "validation_errors": validation_data.get("validation_errors", []),
                "validated_at": validation_data.get("validated_at")
            },
            key=str(event_id)
        )
    
    async def publish_incident_created(self, incident_id: UUID, incident_data: Dict[str, Any]):
        """Publish incident created event"""
        await self.producer.publish_event(
            topic=KafkaTopics.INTEGRITY_EVENTS,
            event_type=KafkaEventTypes.INCIDENT_CREATED,
            data={
                "incident_id": str(incident_id),
                "severity": incident_data.get("severity"),
                "description": incident_data.get("description"),
                "affected_services": incident_data.get("affected_services", []),
                "created_at": incident_data.get("created_at")
            },
            key=str(incident_id)
        )
    
    async def publish_incident_resolved(self, incident_id: UUID, resolution_data: Dict[str, Any]):
        """Publish incident resolved event"""
        await self.producer.publish_event(
            topic=KafkaTopics.INTEGRITY_EVENTS,
            event_type=KafkaEventTypes.INCIDENT_RESOLVED,
            data={
                "incident_id": str(incident_id),
                "resolution_summary": resolution_data.get("resolution_summary"),
                "resolved_at": resolution_data.get("resolved_at"),
                "resolution_time_seconds": resolution_data.get("resolution_time_seconds")
            },
            key=str(incident_id)
        )
