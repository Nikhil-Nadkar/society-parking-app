import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.dependencies.auth import require_admin
from app.models.parking_slot import ParkingSlot
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.parking import ParkingSlotAssign, ParkingSlotCreate, ParkingSlotOut, ParkingSlotUpdate
from app.schemas.payment import PaymentAdminOut, PaymentReject
from app.schemas.user import UserOut

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# ---------- Users ----------

@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.name).all()


# ---------- Parking ----------

@router.get("/parking", response_model=list[ParkingSlotOut])
def list_parking_slots(db: Session = Depends(get_db)):
    return db.query(ParkingSlot).order_by(ParkingSlot.slot_number).all()


@router.post("/parking", response_model=ParkingSlotOut, status_code=status.HTTP_201_CREATED)
def create_parking_slot(payload: ParkingSlotCreate, db: Session = Depends(get_db)):
    existing = db.query(ParkingSlot).filter(ParkingSlot.slot_number == payload.slot_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slot number already exists.")
    slot = ParkingSlot(slot_number=payload.slot_number, type=payload.type)
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.patch("/parking/{slot_id}", response_model=ParkingSlotOut)
def update_parking_slot(slot_id: int, payload: ParkingSlotUpdate, db: Session = Depends(get_db)):
    slot = db.get(ParkingSlot, slot_id)
    if slot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found.")
    if payload.type is not None:
        slot.type = payload.type
    if payload.status is not None:
        slot.status = payload.status
    db.commit()
    db.refresh(slot)
    return slot


@router.post("/parking/{slot_id}/assign", response_model=ParkingSlotOut)
def assign_parking_slot(slot_id: int, payload: ParkingSlotAssign, db: Session = Depends(get_db)):
    slot = db.get(ParkingSlot, slot_id)
    if slot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found.")

    # Unassign whoever currently holds this slot
    if slot.assigned_user_id:
        prev_user = db.get(User, slot.assigned_user_id)
        if prev_user:
            prev_user.parking_slot_id = None

    if payload.user_id is None:
        slot.assigned_user_id = None
        from app.models.parking_slot import SlotStatus

        slot.status = SlotStatus.UNUSED
    else:
        new_user = db.get(User, payload.user_id)
        if new_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        if new_user.parking_slot_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has a parking slot.")
        slot.assigned_user_id = new_user.id
        new_user.parking_slot_id = slot.id
        from app.models.parking_slot import SlotStatus

        slot.status = SlotStatus.ASSIGNED

    db.commit()
    db.refresh(slot)
    return slot


# ---------- Payments ----------

@router.get("/payments", response_model=list[PaymentAdminOut])
def list_payments(status_filter: PaymentStatus | None = None, db: Session = Depends(get_db)):
    query = db.query(Payment).options(joinedload(Payment.user), joinedload(Payment.parking_slot))
    if status_filter is not None:
        query = query.filter(Payment.status == status_filter)
    payments = query.order_by(Payment.created_at.desc()).all()

    return [
        PaymentAdminOut(
            id=p.id,
            user_id=p.user_id,
            amount=p.amount,
            month=p.month,
            year=p.year,
            description=p.description,
            status=p.status,
            created_at=p.created_at,
            approved_at=p.approved_at,
            rejected_at=p.rejected_at,
            rejection_reason=p.rejection_reason,
            user_name=p.user.name if p.user else "",
            room_no=p.user.room_no if p.user else "",
            slot_number=p.parking_slot.slot_number if p.parking_slot else None,
        )
        for p in payments
    ]


@router.get("/payments/{payment_id}/screenshot")
def get_payment_screenshot(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is None or not payment.screenshots:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screenshot not found.")

    latest_screenshot = sorted(payment.screenshots, key=lambda s: s.created_at, reverse=True)[0]
    if not os.path.exists(latest_screenshot.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Screenshot file missing on disk.")

    return FileResponse(latest_screenshot.file_path, media_type="image/jpeg")


@router.post("/payments/{payment_id}/approve", response_model=PaymentAdminOut)
def approve_payment(payment_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending payments can be approved.")

    payment.status = PaymentStatus.APPROVED
    payment.approved_at = datetime.now(timezone.utc)
    payment.approved_by = admin.id
    db.commit()
    db.refresh(payment)

    return PaymentAdminOut(
        **{k: getattr(payment, k) for k in
           ["id", "user_id", "amount", "month", "year", "description", "status", "created_at",
            "approved_at", "rejected_at", "rejection_reason"]},
        user_name=payment.user.name if payment.user else "",
        room_no=payment.user.room_no if payment.user else "",
        slot_number=payment.parking_slot.slot_number if payment.parking_slot else None,
    )


@router.post("/payments/{payment_id}/reject", response_model=PaymentAdminOut)
def reject_payment(payment_id: int, payload: PaymentReject, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending payments can be rejected.")

    payment.status = PaymentStatus.REJECTED
    payment.rejected_at = datetime.now(timezone.utc)
    payment.rejection_reason = payload.rejection_reason
    db.commit()
    db.refresh(payment)

    return PaymentAdminOut(
        **{k: getattr(payment, k) for k in
           ["id", "user_id", "amount", "month", "year", "description", "status", "created_at",
            "approved_at", "rejected_at", "rejection_reason"]},
        user_name=payment.user.name if payment.user else "",
        room_no=payment.user.room_no if payment.user else "",
        slot_number=payment.parking_slot.slot_number if payment.parking_slot else None,
    )
