"""
Shared observability setup module for all services.

This module provides a unified way to initialize tracing and metrics
across all StreamOps services.
"""

import logging
from typing import Optional
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from shared.observability.tracing import TracingConfig
from shared.observability.metrics import MetricsConfig
from shared.observability.middleware import MetricsMiddleware, LoggingMiddleware
from shared.observability.config import ObservabilityConfig

logger = logging.getLogger(__name__)


class ObservabilityManager:
    """Manager for all observability components"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.tracing_config: Optional[TracingConfig] = None
        self.metrics_config: Optional[MetricsConfig] = None
    
    def initialize(self):
        """Initialize all observability components"""
        try:
            # Initialize tracing if enabled
            if ObservabilityConfig.is_tracing_enabled():
                self.tracing_config = TracingConfig(
                    service_name=self.service_name,
                    jaeger_host=ObservabilityConfig.get_jaeger_host(),
                    jaeger_port=ObservabilityConfig.get_jaeger_port()
                )
                self.tracing_config.setup_tracing()
                logger.info("Tracing initialized")
            
            # Initialize metrics if enabled
            if ObservabilityConfig.is_metrics_enabled():
                self.metrics_config = MetricsConfig(service_name=self.service_name)
                logger.info("Metrics initialized")
            
            logger.info(f"Observability initialized for {self.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize observability: {e}")
            raise
    
    def setup_fastapi(
        self,
        app: FastAPI,
        instrument_httpx: bool = True
    ):
        """Setup observability for FastAPI application"""
        try:
            # Add metrics middleware
            if self.metrics_config:
                app.add_middleware(MetricsMiddleware, metrics=self.metrics_config)
            
            # Add logging middleware
            app.add_middleware(LoggingMiddleware)
            
            # Instrument FastAPI for tracing
            if self.tracing_config:
                self.tracing_config.instrument_fastapi(app)
            
            # Instrument HTTPX client
            if self.tracing_config and instrument_httpx:
                self.tracing_config.instrument_httpx()
            
            # Add metrics endpoint
            if self.metrics_config:
                from prometheus_fastapi_instrumentator import Instrumentator
                
                @app.get("/metrics")
                async def metrics():
                    from fastapi.responses import Response
                    return Response(
                        content=self.metrics_config.get_metrics(),
                        media_type="text/plain"
                    )
            
            logger.info("FastAPI observability setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup FastAPI observability: {e}")
            raise
    
    def instrument_database(self, engine: AsyncEngine):
        """Instrument database engine"""
        if self.tracing_config:
            self.tracing_config.instrument_sqlalchemy(engine)
            logger.info("Database instrumentation complete")
    
    def instrument_redis(self, redis_client):
        """Instrument Redis client"""
        if self.tracing_config:
            self.tracing_config.instrument_redis(redis_client)
            logger.info("Redis instrumentation complete")
    
    def get_tracer(self, name: str = __name__):
        """Get a tracer instance"""
        if self.tracing_config:
            return self.tracing_config.get_tracer(name)
        return None
    
    def get_metrics(self) -> Optional[MetricsConfig]:
        """Get metrics config"""
        return self.metrics_config
    
    def shutdown(self):
        """Shutdown all observability components"""
        if self.tracing_config:
            self.tracing_config.shutdown()
            logger.info("Observability shutdown complete")


def setup_observability(
    service_name: str,
    app: FastAPI,
    engine: Optional[AsyncEngine] = None,
    redis_client=None
) -> ObservabilityManager:
    """
    Convenience function to setup observability for a service
    
    Args:
        service_name: Name of the service
        app: FastAPI application instance
        engine: Optional SQLAlchemy engine
        redis_client: Optional Redis client
        
    Returns:
        ObservabilityManager instance
    """
    manager = ObservabilityManager(service_name)
    manager.initialize()
    manager.setup_fastapi(app)
    
    if engine:
        manager.instrument_database(engine)
    
    if redis_client:
        manager.instrument_redis(redis_client)
    
    return manager
