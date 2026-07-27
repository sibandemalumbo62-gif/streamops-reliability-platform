import os
from typing import Optional


class KafkaConfig:
    """Kafka configuration"""
    
    @staticmethod
    def get_bootstrap_servers() -> str:
        """Get Kafka bootstrap servers from environment"""
        return os.getenv(
            'KAFKA_BOOTSTRAP_SERVERS',
            'localhost:9092'
        )
    
    @staticmethod
    def get_consumer_group_id(service_name: str) -> str:
        """Get consumer group ID for a service"""
        return os.getenv(
            'KAFKA_CONSUMER_GROUP_ID',
            f'{service_name}-group'
        )
    
    @staticmethod
    def get_topic(topic_name: str) -> str:
        """Get topic name with optional prefix"""
        prefix = os.getenv('KAFKA_TOPIC_PREFIX', '')
        return f"{prefix}{topic_name}" if prefix else topic_name


# Topic definitions
class KafkaTopics:
    """Kafka topic names"""
    
    USER_EVENTS = "user-events"
    CONTENT_EVENTS = "content-events"
    PLAYBACK_EVENTS = "playback-events"
    RECOMMENDATION_EVENTS = "recommendation-events"
    NOTIFICATION_EVENTS = "notification-events"
    INTEGRITY_EVENTS = "integrity-events"


# Event type definitions
class KafkaEventTypes:
    """Kafka event type names"""
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    
    # Content events
    CONTENT_CREATED = "content.created"
    CONTENT_UPDATED = "content.updated"
    CONTENT_DELETED = "content.deleted"
    CONTENT_PUBLISHED = "content.published"
    
    # Playback events
    PLAYBACK_STARTED = "playback.started"
    PLAYBACK_PAUSED = "playback.paused"
    PLAYBACK_RESUMED = "playback.resumed"
    PLAYBACK_STOPPED = "playback.stopped"
    PLAYBACK_COMPLETED = "playback.completed"
    
    # Recommendation events
    RECOMMENDATION_GENERATED = "recommendation.generated"
    PREFERENCE_UPDATED = "preference.updated"
    
    # Notification events
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_READ = "notification.read"
    
    # Integrity events
    EVENT_VALIDATED = "event.validated"
    INCIDENT_CREATED = "incident.created"
    INCIDENT_RESOLVED = "incident.resolved"
