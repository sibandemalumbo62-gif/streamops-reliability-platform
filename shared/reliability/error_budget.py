"""
Error Budget implementation.

Error Budget is the amount of error that a service can tolerate
within a given time period while still meeting its SLO.
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta

from shared.reliability.slo import SLO, SLOPeriod

logger = logging.getLogger(__name__)


class ErrorBudget:
    """Error Budget for a service"""
    
    def __init__(self, slo: SLO):
        self.slo = slo
        self.budget_remaining: float = 100.0  # Percentage
        self.budget_consumed: float = 0.0  # Percentage
        self.burn_rate: float = 0.0  # Percentage per day
        self.alert_threshold: float = 10.0  # Alert when 10% budget remains
        self.history: List[Dict] = []
    
    def calculate_budget_from_slo(self) -> float:
        """Calculate total error budget from SLO target"""
        # Error budget = 100% - SLO target
        # For availability SLO of 99.9%, error budget is 0.1%
        if self.slo.sli_name == 'availability':
            return 100.0 - self.slo.target_value
        elif self.slo.sli_name == 'error_rate':
            return self.slo.target_value
        else:
            # For other SLOs, use a default budget
            return 5.0  # 5% budget for non-critical SLOs
    
    def update_budget(self, current_sli_value: float):
        """Update error budget based on current SLI value"""
        total_budget = self.calculate_budget_from_slo()
        
        # Calculate how much of the budget has been consumed
        if self.slo.sli_name == 'availability':
            # For availability, consumed = 100 - current value
            self.budget_consumed = 100.0 - current_sli_value
        elif self.slo.sli_name == 'error_rate':
            # For error rate, consumed = current value
            self.budget_consumed = current_sli_value
        else:
            # For other SLOs, calculate based on deviation from target
            deviation = abs(current_sli_value - self.slo.target_value)
            self.budget_consumed = (deviation / self.slo.target_value) * 100
        
        # Ensure budget doesn't exceed total
        self.budget_consumed = min(self.budget_consumed, total_budget)
        self.budget_remaining = total_budget - self.budget_consumed
        
        # Calculate burn rate
        self._calculate_burn_rate()
        
        # Record in history
        self.history.append({
            'timestamp': datetime.utcnow(),
            'budget_remaining': self.budget_remaining,
            'budget_consumed': self.budget_consumed,
            'burn_rate': self.burn_rate
        })
        
        logger.info(
            f"Error Budget for {self.slo.name}: "
            f"remaining={self.budget_remaining:.2f}%, "
            f"consumed={self.budget_consumed:.2f}%, "
            f"burn_rate={self.burn_rate:.2f}%/day"
        )
    
    def _calculate_burn_rate(self):
        """Calculate the rate at which budget is being consumed"""
        if len(self.history) < 2:
            self.burn_rate = 0.0
            return
        
        # Get last 24 hours of data
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent = [
            h for h in self.history
            if h['timestamp'] >= cutoff
        ]
        
        if len(recent) < 2:
            self.burn_rate = 0.0
            return
        
        # Calculate burn rate from first and last measurements
        first = recent[0]
        last = recent[-1]
        
        time_diff_hours = (last['timestamp'] - first['timestamp']).total_seconds() / 3600
        if time_diff_hours > 0:
            budget_diff = first['budget_remaining'] - last['budget_remaining']
            self.burn_rate = (budget_diff / time_diff_hours) * 24  # Convert to per day
        else:
            self.burn_rate = 0.0
    
    def is_budget_exhausted(self) -> bool:
        """Check if error budget is exhausted"""
        return self.budget_remaining <= 0
    
    def is_alert_triggered(self) -> bool:
        """Check if alert should be triggered"""
        return self.budget_remaining <= self.alert_threshold
    
    def get_time_until_exhaustion(self) -> Optional[float]:
        """Estimate days until budget exhaustion"""
        if self.burn_rate <= 0:
            return None
        return self.budget_remaining / self.burn_rate


class ErrorBudgetManager:
    """Manager for error budgets across all SLOs"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.error_budgets: Dict[str, ErrorBudget] = {}
    
    def add_error_budget(self, error_budget: ErrorBudget):
        """Add an error budget"""
        self.error_budgets[error_budget.slo.name] = error_budget
    
    def update_all_budgets(self, sli_values: Dict[str, float]):
        """Update all error budgets based on current SLI values"""
        for budget in self.error_budgets.values():
            sli_value = sli_values.get(budget.slo.sli_name)
            if sli_value is not None:
                budget.update_budget(sli_value)
    
    def get_critical_budgets(self) -> List[str]:
        """Get budgets that are in critical state"""
        critical = []
        for name, budget in self.error_budgets.items():
            if budget.is_alert_triggered():
                critical.append(name)
        return critical
    
    def get_exhausted_budgets(self) -> List[str]:
        """Get budgets that are exhausted"""
        exhausted = []
        for name, budget in self.error_budgets.items():
            if budget.is_budget_exhausted():
                exhausted.append(name)
        return exhausted
    
    def get_budget_summary(self) -> Dict[str, Dict]:
        """Get summary of all error budgets"""
        return {
            name: {
                'remaining': budget.budget_remaining,
                'consumed': budget.budget_consumed,
                'burn_rate': budget.burn_rate,
                'is_critical': budget.is_alert_triggered(),
                'is_exhausted': budget.is_budget_exhausted(),
                'days_until_exhaustion': budget.get_time_until_exhaustion()
            }
            for name, budget in self.error_budgets.items()
        }
