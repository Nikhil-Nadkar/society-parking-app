from calendar import monthrange
from datetime import date, datetime, timezone
from enum import Enum

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.payment import Payment, PaymentStatus


class DisplayStatus(str, Enum):
    """Status as shown on the dashboard. Distinct from the raw DB PaymentStatus because
    "no submission yet" and "submitted, awaiting admin" are different UI states even
    though neither has an APPROVED/REJECTED row yet."""

    APPROVED = "approved"        # green
    PENDING = "pending"          # orange - submitted, waiting for admin
    OVERDUE = "overdue"          # red - nothing valid submitted, past grace period
    REJECTED = "rejected"        # red - admin rejected, still within grace / resubmittable
    DUE = "due"                  # neutral - current/previous period, not yet submitted, not overdue
    NOT_DUE = "not_due"          # future period


def due_date_for_period(month: int, year: int) -> date:
    """Due date is the last day of that month; OVERDUE kicks in PAYMENT_GRACE_DAYS after that."""
    last_day = monthrange(year, month)[1]
    return date(year, month, last_day)


def is_period_overdue(month: int, year: int, today: date | None = None) -> bool:
    today = today or datetime.now(timezone.utc).date()
    due = due_date_for_period(month, year)
    days_since_due = (today - due).days
    return days_since_due > settings.PAYMENT_GRACE_DAYS


def is_period_submittable(month: int, year: int, today: date | None = None) -> bool:
    """Only the current month, or the previous month if still unpaid, may receive new submissions."""
    today = today or datetime.now(timezone.utc).date()
    current_month, current_year = today.month, today.year

    if month == current_month and year == current_year:
        return True

    prev_month = 12 if current_month == 1 else current_month - 1
    prev_year = current_year - 1 if current_month == 1 else current_year

    return month == prev_month and year == prev_year


def resolve_display_status(payment: Payment | None, month: int, year: int, today: date | None = None) -> DisplayStatus:
    today = today or datetime.now(timezone.utc).date()
    current_month, current_year = today.month, today.year
    period = (year, month)
    overdue = is_period_overdue(month, year, today)

    if payment is not None:
        if payment.status == PaymentStatus.APPROVED:
            return DisplayStatus.APPROVED
        if payment.status == PaymentStatus.PENDING:
            return DisplayStatus.PENDING
        if payment.status == PaymentStatus.REJECTED:
            return DisplayStatus.OVERDUE if overdue else DisplayStatus.REJECTED

    if period > (current_year, current_month):
        return DisplayStatus.NOT_DUE

    return DisplayStatus.OVERDUE if overdue else DisplayStatus.DUE


def get_latest_payment_for_period(db: Session, user_id: int, month: int, year: int) -> Payment | None:
    return (
        db.query(Payment)
        .filter(Payment.user_id == user_id, Payment.month == month, Payment.year == year)
        .order_by(Payment.created_at.desc())
        .first()
    )


def has_active_payment(db: Session, user_id: int, month: int, year: int) -> bool:
    """Active = pending or approved. A rejected or overdue period can still receive a new submission."""
    return (
        db.query(Payment)
        .filter(
            Payment.user_id == user_id,
            Payment.month == month,
            Payment.year == year,
            Payment.status.in_([PaymentStatus.PENDING, PaymentStatus.APPROVED]),
        )
        .first()
        is not None
    )
