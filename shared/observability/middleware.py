import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from shared.observability.metrics import MetricsConfig

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect metrics for all HTTP requests"""
    
    def __init__(self, app, metrics: MetricsConfig):
        super().__init__(app)
        self.metrics = metrics
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        self.metrics.increment_active_requests()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record request metrics
            self.metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_error(type(e).__name__)
            self.metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status=500,
                duration=duration
            )
            raise
            
        finally:
            self.metrics.decrement_active_requests()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Duration: {duration:.3f}s"
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"- Error: {str(e)} - Duration: {duration:.3f}s"
            )
            raise
