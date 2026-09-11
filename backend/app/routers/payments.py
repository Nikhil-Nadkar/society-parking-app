from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.payment import Payment, PaymentStatus
from app.models.payment_screenshot import PaymentScreenshot
from app.models.user import User
from app.schemas.payment import PaymentMonthStatus, PaymentOut
from app.services.image_service import validate_and_compress_screenshot
from app.services.payment_status_service import (
    get_latest_payment_for_period,
    has_active_payment,
    is_period_submittable,
    resolve_display_status,
)

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get("/dashboard/{year}", response_model=list[PaymentMonthStatus])
def get_year_dashboard(year: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns the 12-month status grid for the given year for the logged-in user."""
    today = datetime.now(timezone.utc).date()
    results: list[PaymentMonthStatus] = []
    for month in range(1, 13):
        payment = get_latest_payment_for_period(db, current_user.id, month, year)
        display_status = resolve_display_status(payment, month, year, today)
        results.append(
            PaymentMonthStatus(
                month=month,
                year=year,
                status=display_status.value,
                payment_id=payment.id if payment else None,
            )
        )
    return results


@router.get("/me", response_model=list[PaymentOut])
def list_my_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.year.desc(), Payment.month.desc())
        .all()
    )


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def submit_payment(
    month: int = Form(..., ge=1, le=12),
    year: int = Form(..., ge=2020, le=2100),
    description: str | None = Form(default=None),
    screenshot: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not is_period_submittable(month, year):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only the current month or previous month (if still unpaid) can be submitted.",
        )

    if has_active_payment(db, current_user.id, month, year):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A payment for this month is already pending or approved.",
        )

    file_path = await validate_and_compress_screenshot(screenshot)

    payment = Payment(
        user_id=current_user.id,
        parking_slot_id=current_user.parking_slot_id,
        amount=settings.DEFAULT_PAYMENT_AMOUNT,
        month=month,
        year=year,
        description=description,
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    db.flush()

    db.add(PaymentScreenshot(payment_id=payment.id, user_id=current_user.id, file_path=file_path))
    db.commit()
    db.refresh(payment)

    return payment
