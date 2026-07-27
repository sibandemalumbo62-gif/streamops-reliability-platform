import logging
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

logger = logging.getLogger(__name__)


class TracingConfig:
    """OpenTelemetry tracing configuration"""
    
    def __init__(
        self,
        service_name: str,
        jaeger_host: str = "localhost",
        jaeger_port: int = 6831
    ):
        self.service_name = service_name
        self.jaeger_host = jaeger_host
        self.jaeger_port = jaeger_port
        self._provider: Optional[TracerProvider] = None
    
    def setup_tracing(self):
        """Initialize OpenTelemetry tracing"""
        try:
            # Create resource
            resource = Resource.create({
                SERVICE_NAME: self.service_name,
                "service.version": "1.0.0",
                "deployment.environment": "production"
            })
            
            # Create tracer provider
            self._provider = TracerProvider(resource=resource)
            
            # Configure Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=self.jaeger_host,
                agent_port=self.jaeger_port,
            )
            
            # Add span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            self._provider.add_span_processor(span_processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(self._provider)
            
            logger.info(f"Tracing initialized for service: {self.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
            raise
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application"""
        try:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumentation enabled")
        except Exception as e:
            logger.error(f"Failed to instrument FastAPI: {e}")
    
    def instrument_httpx(self):
        """Instrument HTTPX client"""
        try:
            HTTPXClientInstrumentor().instrument()
            logger.info("HTTPX instrumentation enabled")
        except Exception as e:
            logger.error(f"Failed to instrument HTTPX: {e}")
    
    def instrument_sqlalchemy(self, engine):
        """Instrument SQLAlchemy engine"""
        try:
            SQLAlchemyInstrumentor().instrument(engine=engine)
            logger.info("SQLAlchemy instrumentation enabled")
        except Exception as e:
            logger.error(f"Failed to instrument SQLAlchemy: {e}")
    
    def instrument_redis(self, redis_client):
        """Instrument Redis client"""
        try:
            RedisInstrumentor().instrument_client(redis_client)
            logger.info("Redis instrumentation enabled")
        except Exception as e:
            logger.error(f"Failed to instrument Redis: {e}")
    
    def get_tracer(self, name: str = __name__):
        """Get a tracer instance"""
        return trace.get_tracer(name)
    
    def shutdown(self):
        """Shutdown tracing provider"""
        if self._provider:
            self._provider.shutdown()
            logger.info("Tracing shutdown complete")


def get_current_span():
    """Get the current span from context"""
    return trace.get_current_span()


def add_span_exception(exception: Exception):
    """Add exception to current span"""
    span = get_current_span()
    if span:
        span.record_exception(exception)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))


def add_span_attributes(attributes: dict):
    """Add attributes to current span"""
    span = get_current_span()
    if span:
        span.set_attributes(attributes)
