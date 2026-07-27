from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .reliability_model import ReliabilityMetric
from .alert_model import Alert
from .error_budget_model import ErrorBudget

from .reliability_metrics import (
    reliability_score_metric,
    error_budget_metric,
    active_alert_metric
)


router = APIRouter(
    prefix="/internal",
    tags=["Metrics"]
)


@router.get("/refresh-metrics")
def refresh_metrics(
    db: Session = Depends(get_db)
):

    reliability = db.query(
        ReliabilityMetric
    ).all()


    for item in reliability:

        reliability_score_metric.labels(
            service=item.service
        ).set(
            item.reliability_score
        )


    budgets = db.query(
        ErrorBudget
    ).all()


    for budget in budgets:

        error_budget_metric.labels(
            service=budget.service_name
        ).set(
            budget.remaining_budget
        )


    alerts = db.query(Alert).filter(
        Alert.resolved == False
    ).all()


    counts = {}

    for alert in alerts:

        counts[alert.service] = (
            counts.get(alert.service,0)+1
        )


    for service,count in counts.items():

        active_alert_metric.labels(
            service=service
        ).set(count)


    return {
        "status":"metrics updated"
    }