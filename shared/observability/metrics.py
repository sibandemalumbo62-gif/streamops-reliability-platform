import logging
import time
from typing import Optional, Callable
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
from functools import wraps

logger = logging.getLogger(__name__)


class MetricsConfig:
    """Prometheus metrics configuration"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.registry = CollectorRegistry()
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Initialize Prometheus metrics"""
        # Info metric
        self.info = Info(
            'service_info',
            'Service information',
            registry=self.registry
        )
        self.info.info({
            'service': self.service_name,
            'version': '1.0.0'
        })
        
        # Request counter
        self.request_counter = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        # Request latency histogram
        self.request_latency = Histogram(
            'http_request_duration_seconds',
            'HTTP request latency',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Active requests gauge
        self.active_requests = Gauge(
            'http_requests_active',
            'Active HTTP requests',
            registry=self.registry
        )
        
        # Error counter
        self.error_counter = Counter(
            'errors_total',
            'Total errors',
            ['error_type'],
            registry=self.registry
        )
        
        # Database operation counter
        self.db_operations = Counter(
            'db_operations_total',
            'Total database operations',
            ['operation', 'table'],
            registry=self.registry
        )
        
        # Database operation latency
        self.db_latency = Histogram(
            'db_operation_duration_seconds',
            'Database operation latency',
            ['operation', 'table'],
            registry=self.registry
        )
        
        # Kafka message counter
        self.kafka_messages = Counter(
            'kafka_messages_total',
            'Total Kafka messages',
            ['topic', 'direction'],  # direction: produce/consume
            registry=self.registry
        )
        
        # Cache operations
        self.cache_operations = Counter(
            'cache_operations_total',
            'Total cache operations',
            ['operation', 'status'],  # operation: get/set/delete, status: hit/miss
            registry=self.registry
        )
        
        logger.info(f"Metrics initialized for service: {self.service_name}")
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        self.request_counter.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        self.request_latency.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def increment_active_requests(self):
        """Increment active requests counter"""
        self.active_requests.inc()
    
    def decrement_active_requests(self):
        """Decrement active requests counter"""
        self.active_requests.dec()
    
    def record_error(self, error_type: str):
        """Record an error"""
        self.error_counter.labels(error_type=error_type).inc()
    
    def record_db_operation(self, operation: str, table: str, duration: float):
        """Record database operation"""
        self.db_operations.labels(
            operation=operation,
            table=table
        ).inc()
        self.db_latency.labels(
            operation=operation,
            table=table
        ).observe(duration)
    
    def record_kafka_message(self, topic: str, direction: str):
        """Record Kafka message"""
        self.kafka_messages.labels(
            topic=topic,
            direction=direction
        ).inc()
    
    def record_cache_operation(self, operation: str, status: str):
        """Record cache operation"""
        self.cache_operations.labels(
            operation=operation,
            status=status
        ).inc()
    
    def get_metrics(self) -> bytes:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry)


def track_requests(metrics: MetricsConfig):
    """Decorator to track HTTP requests"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            metrics.increment_active_requests()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Try to get request info from FastAPI context
                # This will be populated by the middleware
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_error(type(e).__name__)
                raise
                
            finally:
                metrics.decrement_active_requests()
        
        return wrapper
    return decorator


def track_db_operations(metrics: MetricsConfig):
    """Decorator to track database operations"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Extract table name from function name or context
                table_name = getattr(func, '__table__', 'unknown')
                operation = func.__name__.split('_')[0]  # e.g., get_user -> get
                
                metrics.record_db_operation(operation, table_name, duration)
                return result
                
            except Exception as e:
                metrics.record_error(type(e).__name__)
                raise
        
        return wrapper
    return decorator
