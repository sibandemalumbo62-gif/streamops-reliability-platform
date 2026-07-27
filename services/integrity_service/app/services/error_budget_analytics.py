from sqlalchemy.orm import Session

from ..error_budget_model import ErrorBudget


def get_error_budget(
    db: Session,
    service_name: str
):

    budget = (
        db.query(ErrorBudget)
        .filter(
            ErrorBudget.service_name == service_name
        )
        .order_by(
            ErrorBudget.id.desc()
        )
        .first()
    )


    if not budget:
        return {
            "service": service_name,
            "status": "NO_DATA"
        }


    if budget.remaining_budget <= 0:

        status = "EXHAUSTED"

    elif budget.remaining_budget < 50:

        status = "WARNING"

    else:

        status = "HEALTHY"


    return {
        "service": budget.service_name,
        "slo_target": budget.slo_target,
        "availability": budget.availability,
        "remaining_budget": budget.remaining_budget,
        "status": status
    }