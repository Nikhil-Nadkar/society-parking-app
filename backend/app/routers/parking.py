from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.parking_slot import ParkingSlot
from app.models.user import User
from app.schemas.parking import ParkingSlotWithPaymentStatus
from app.services.payment_status_service import get_latest_payment_for_period, resolve_display_status

router = APIRouter(prefix="/api/parking", tags=["parking"])


@router.get("/map", response_model=list[ParkingSlotWithPaymentStatus])
def get_parking_map(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns every slot with a payment_status derived from the assigned resident's
    current-month payment, so the 2D map can color slots without extra client calls."""
    today = datetime.now(timezone.utc).date()
    slots = db.query(ParkingSlot).order_by(ParkingSlot.slot_number).all()

    results: list[ParkingSlotWithPaymentStatus] = []
    for slot in slots:
        payment_status = None
        resident_name = None
        if slot.assigned_user_id:
            payment = get_latest_payment_for_period(db, slot.assigned_user_id, today.month, today.year)
            payment_status = resolve_display_status(payment, today.month, today.year, today).value
            if slot.assigned_user:
                resident_name = slot.assigned_user.name

        results.append(
            ParkingSlotWithPaymentStatus(
                id=slot.id,
                slot_number=slot.slot_number,
                type=slot.type,
                status=slot.status,
                assigned_user_id=slot.assigned_user_id,
                payment_status=payment_status,
                resident_name=resident_name,
            )
        )

    return results
