"""
Service Level Indicators (SLIs) implementation.

SLIs are quantitative measures of service performance.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class SLIMetricType(Enum):
    """Types of SLI metrics"""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    SATISFACTION = "satisfaction"


class SLI:
    """Service Level Indicator"""
    
    def __init__(
        self,
        name: str,
        metric_type: SLIMetricType,
        description: str,
        unit: str = "percent"
    ):
        self.name = name
        self.metric_type = metric_type
        self.description = description
        self.unit = unit
        self.measurements: List[Dict] = []
    
    def record_measurement(self, value: float, timestamp: Optional[datetime] = None):
        """Record a measurement"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        self.measurements.append({
            'value': value,
            'timestamp': timestamp
        })
        
        logger.debug(f"Recorded SLI measurement: {self.name} = {value} {self.unit}")
    
    def get_current_value(self) -> Optional[float]:
        """Get the most recent measurement"""
        if not self.measurements:
            return None
        return self.measurements[-1]['value']
    
    def get_average(self, window_minutes: int = 60) -> Optional[float]:
        """Get average value over time window"""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent = [
            m['value'] for m in self.measurements
            if m['timestamp'] >= cutoff
        ]
        
        if not recent:
            return None
        
        return sum(recent) / len(recent)
    
    def get_percentile(self, percentile: float, window_minutes: int = 60) -> Optional[float]:
        """Get percentile value over time window"""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent = sorted([
            m['value'] for m in self.measurements
            if m['timestamp'] >= cutoff
        ])
        
        if not recent:
            return None
        
        index = int(len(recent) * percentile / 100)
        return recent[index]


class SLICollector:
    """Collector for SLI metrics"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.slis: Dict[str, SLI] = {}
        self._setup_default_slis()
    
    def _setup_default_slis(self):
        """Setup default SLIs for the service"""
        # Availability SLI
        self.slis['availability'] = SLI(
            name='availability',
            metric_type=SLIMetricType.AVAILABILITY,
            description='Percentage of successful requests',
            unit='percent'
        )
        
        # Latency SLIs
        self.slis['latency_p50'] = SLI(
            name='latency_p50',
            metric_type=SLIMetricType.LATENCY,
            description='50th percentile request latency',
            unit='milliseconds'
        )
        self.slis['latency_p95'] = SLI(
            name='latency_p95',
            metric_type=SLIMetricType.LATENCY,
            description='95th percentile request latency',
            unit='milliseconds'
        )
        self.slis['latency_p99'] = SLI(
            name='latency_p99',
            metric_type=SLIMetricType.LATENCY,
            description='99th percentile request latency',
            unit='milliseconds'
        )
        
        # Error Rate SLI
        self.slis['error_rate'] = SLI(
            name='error_rate',
            metric_type=SLIMetricType.ERROR_RATE,
            description='Percentage of requests that result in errors',
            unit='percent'
        )
        
        # Throughput SLI
        self.slis['throughput'] = SLI(
            name='throughput',
            metric_type=SLIMetricType.THROUGHPUT,
            description='Requests per second',
            unit='rps'
        )
    
    def record_request(
        self,
        success: bool,
        latency_ms: float,
        timestamp: Optional[datetime] = None
    ):
        """Record a request for SLI calculation"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # This would typically be calculated from aggregated metrics
        # For now, we'll record individual measurements
        pass
    
    def calculate_availability(self, success_count: int, total_count: int) -> float:
        """Calculate availability percentage"""
        if total_count == 0:
            return 100.0
        return (success_count / total_count) * 100
    
    def calculate_error_rate(self, error_count: int, total_count: int) -> float:
        """Calculate error rate percentage"""
        if total_count == 0:
            return 0.0
        return (error_count / total_count) * 100
    
    def get_sli(self, name: str) -> Optional[SLI]:
        """Get an SLI by name"""
        return self.slis.get(name)
    
    def get_all_slis(self) -> Dict[str, SLI]:
        """Get all SLIs"""
        return self.slis
    
    def record_sli_value(self, name: str, value: float):
        """Record a value for a specific SLI"""
        sli = self.get_sli(name)
        if sli:
            sli.record_measurement(value)
        else:
            logger.warning(f"SLI {name} not found")
