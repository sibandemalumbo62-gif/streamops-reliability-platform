from sqlalchemy.orm import Session

from ..error_budget_model import ErrorBudget


def calculate_error_budget(
    db: Session,
    service_name: str,
    availability: float,
    slo_target: float = 99.9
):

    allowed_failure = 100 - slo_target

    consumed_failure = 100 - availability

    remaining = allowed_failure - consumed_failure

    if remaining < 0:
        remaining = 0


    budget = ErrorBudget(
        service_name=service_name,
        slo_target=slo_target,
        availability=availability,
        remaining_budget=remaining
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    return budget