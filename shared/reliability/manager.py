"""
Unified Reliability Manager.

This module provides a unified interface for managing SLIs, SLOs, and Error Budgets.
"""

import logging
from typing import Dict, Optional
from datetime import datetime

from shared.reliability.sli import SLICollector
from shared.reliability.slo import SLOManager
from shared.reliability.error_budget import ErrorBudgetManager, ErrorBudget

logger = logging.getLogger(__name__)


class ReliabilityManager:
    """Unified manager for all reliability components"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.sli_collector = SLICollector(service_name)
        self.slo_manager = SLOManager(service_name)
        self.error_budget_manager = ErrorBudgetManager(service_name)
        
        # Setup error budgets for all SLOs
        self._setup_error_budgets()
    
    def _setup_error_budgets(self):
        """Setup error budgets for all SLOs"""
        for slo in self.slo_manager.get_all_slos().values():
            error_budget = ErrorBudget(slo)
            self.error_budget_manager.add_error_budget(error_budget)
    
    def record_metric(self, sli_name: str, value: float):
        """Record a metric value"""
        self.sli_collector.record_sli_value(sli_name, value)
        self.slo_manager.update_slo_compliance(sli_name, value)
    
    def update_all_metrics(self, sli_values: Dict[str, float]):
        """Update all metrics at once"""
        for sli_name, value in sli_values.items():
            self.record_metric(sli_name, value)
        
        # Update error budgets
        self.error_budget_manager.update_all_budgets(sli_values)
    
    def get_sli_status(self) -> Dict:
        """Get current SLI status"""
        status = {}
        for name, sli in self.sli_collector.get_all_slis().items():
            status[name] = {
                'current_value': sli.get_current_value(),
                'average': sli.get_average(),
                'description': sli.description,
                'unit': sli.unit
            }
        return status
    
    def get_slo_status(self) -> Dict:
        """Get current SLO status"""
        return self.slo_manager.get_overall_compliance()
    
    def get_error_budget_status(self) -> Dict:
        """Get current error budget status"""
        return self.error_budget_manager.get_budget_summary()
    
    def get_health_report(self) -> Dict:
        """Get comprehensive health report"""
        return {
            'service': self.service_name,
            'timestamp': datetime.utcnow().isoformat(),
            'slis': self.get_sli_status(),
            'slos': self.get_slo_status(),
            'error_budgets': self.get_error_budget_status(),
            'violating_slos': self.slo_manager.get_violating_slos(),
            'critical_budgets': self.error_budget_manager.get_critical_budgets(),
            'exhausted_budgets': self.error_budget_manager.get_exhausted_budgets()
        }
    
    def is_healthy(self) -> bool:
        """Check if service is healthy based on SLOs and error budgets"""
        # Service is healthy if no SLOs are violating and no budgets are exhausted
        return (
            len(self.slo_manager.get_violating_slos()) == 0 and
            len(self.error_budget_manager.get_exhausted_budgets()) == 0
        )
