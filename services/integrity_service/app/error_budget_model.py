from sqlalchemy import Column, Integer, String, Float
from .database import Base


class ErrorBudget(Base):

    __tablename__ = "error_budgets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    service_name = Column(
        String,
        nullable=False
    )

    slo_target = Column(
        Float,
        nullable=False
    )

    availability = Column(
        Float,
        nullable=False
    )

    remaining_budget = Column(
        Float,
        nullable=False
    )