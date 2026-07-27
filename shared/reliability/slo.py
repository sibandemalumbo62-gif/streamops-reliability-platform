"""
Service Level Objectives (SLOs) implementation.

SLOs are target values for SLIs that the service aims to meet.
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from enum import Enum

from shared.reliability.sli import SLI, SLIMetricType

logger = logging.getLogger(__name__)


class SLOPeriod(Enum):
    """Time periods for SLO evaluation"""
    ROLLING_DAY = "rolling_day"
    ROLLING_WEEK = "rolling_week"
    ROLLING_MONTH = "rolling_month"
    CALENDAR_DAY = "calendar_day"
    CALENDAR_WEEK = "calendar_week"
    CALENDAR_MONTH = "calendar_month"


class SLO:
    """Service Level Objective"""
    
    def __init__(
        self,
        name: str,
        sli_name: str,
        target_value: float,
        period: SLOPeriod,
        description: str
    ):
        self.name = name
        self.sli_name = sli_name
        self.target_value = target_value
        self.period = period
        self.description = description
        self.compliance_history: List[Dict] = []
    
    def check_compliance(self, current_value: float) -> bool:
        """Check if current value meets the SLO target"""
        return current_value >= self.target_value
    
    def calculate_compliance_percentage(self, current_value: float) -> float:
        """Calculate how close the current value is to the target"""
        if self.target_value == 0:
            return 100.0
        return (current_value / self.target_value) * 100
    
    def record_compliance(
        self,
        current_value: float,
        timestamp: Optional[datetime] = None
    ):
        """Record compliance check result"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        is_compliant = self.check_compliance(current_value)
        compliance_pct = self.calculate_compliance_percentage(current_value)
        
        self.compliance_history.append({
            'timestamp': timestamp,
            'current_value': current_value,
            'target_value': self.target_value,
            'is_compliant': is_compliant,
            'compliance_percentage': compliance_pct
        })
        
        logger.info(
            f"SLO {self.name}: current={current_value:.2f}, "
            f"target={self.target_value:.2f}, compliant={is_compliant}"
        )
    
    def get_compliance_rate(self, window_days: int = 30) -> Optional[float]:
        """Get compliance rate over time window"""
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        recent = [
            c for c in self.compliance_history
            if c['timestamp'] >= cutoff
        ]
        
        if not recent:
            return None
        
        compliant_count = sum(1 for c in recent if c['is_compliant'])
        return (compliant_count / len(recent)) * 100


class SLOManager:
    """Manager for Service Level Objectives"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.slos: Dict[str, SLO] = {}
        self._setup_default_slos()
    
    def _setup_default_slos(self):
        """Setup default SLOs for the service"""
        # Availability SLO - 99.9% uptime
        self.slos['availability'] = SLO(
            name='availability',
            sli_name='availability',
            target_value=99.9,
            period=SLOPeriod.ROLLING_MONTH,
            description='99.9% availability over rolling 30 days'
        )
        
        # Latency SLOs
        self.slos['latency_p50'] = SLO(
            name='latency_p50',
            sli_name='latency_p50',
            target_value=200,  # 200ms
            period=SLOPeriod.ROLLING_WEEK,
            description='P50 latency under 200ms'
        )
        
        self.slos['latency_p95'] = SLO(
            name='latency_p95',
            sli_name='latency_p95',
            target_value=500,  # 500ms
            period=SLOPeriod.ROLLING_WEEK,
            description='P95 latency under 500ms'
        )
        
        self.slos['latency_p99'] = SLO(
            name='latency_p99',
            sli_name='latency_p99',
            target_value=1000,  # 1000ms
            period=SLOPeriod.ROLLING_WEEK,
            description='P99 latency under 1000ms'
        )
        
        # Error Rate SLO
        self.slos['error_rate'] = SLO(
            name='error_rate',
            sli_name='error_rate',
            target_value=0.1,  # 0.1% error rate
            period=SLOPeriod.ROLLING_WEEK,
            description='Error rate below 0.1%'
        )
    
    def get_slo(self, name: str) -> Optional[SLO]:
        """Get an SLO by name"""
        return self.slos.get(name)
    
    def get_all_slos(self) -> Dict[str, SLO]:
        """Get all SLOs"""
        return self.slos
    
    def update_slo_compliance(self, sli_name: str, current_value: float):
        """Update compliance for an SLO based on current SLI value"""
        for slo in self.slos.values():
            if slo.sli_name == sli_name:
                slo.record_compliance(current_value)
    
    def get_overall_compliance(self) -> Dict[str, float]:
        """Get overall compliance status for all SLOs"""
        return {
            name: slo.get_compliance_rate()
            for name, slo in self.slos.items()
        }
    
    def get_violating_slos(self) -> List[str]:
        """Get list of SLOs currently violating their targets"""
        violating = []
        for name, slo in self.slos.items():
            if slo.compliance_history:
                latest = slo.compliance_history[-1]
                if not latest['is_compliant']:
                    violating.append(name)
        return violating
