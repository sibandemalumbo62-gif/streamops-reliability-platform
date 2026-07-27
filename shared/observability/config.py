import os
from typing import Optional


class ObservabilityConfig:
    """Configuration for observability components"""
    
    @staticmethod
    def get_jaeger_host() -> str:
        """Get Jaeger host from environment"""
        return os.getenv('JAEGER_HOST', 'localhost')
    
    @staticmethod
    def get_jaeger_port() -> int:
        """Get Jaeger port from environment"""
        return int(os.getenv('JAEGER_PORT', '6831'))
    
    @staticmethod
    def get_prometheus_port() -> int:
        """Get Prometheus metrics port from environment"""
        return int(os.getenv('PROMETHEUS_PORT', '9090'))
    
    @staticmethod
    def is_tracing_enabled() -> bool:
        """Check if tracing is enabled"""
        return os.getenv('TRACING_ENABLED', 'true').lower() == 'true'
    
    @staticmethod
    def is_metrics_enabled() -> bool:
        """Check if metrics collection is enabled"""
        return os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
    
    @staticmethod
    def get_service_name() -> Optional[str]:
        """Get service name from environment"""
        return os.getenv('SERVICE_NAME')
    
    @staticmethod
    def get_service_version() -> str:
        """Get service version from environment"""
        return os.getenv('SERVICE_VERSION', '1.0.0')
    
    @staticmethod
    def get_environment() -> str:
        """Get deployment environment"""
        return os.getenv('ENVIRONMENT', 'development')
