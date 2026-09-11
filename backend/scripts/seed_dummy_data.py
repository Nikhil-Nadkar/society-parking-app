"""Seeds realistic test data: 1 admin + 5 residents with a mix of payment
states, so you can immediately test the dashboard, parking map, and the
admin approval workflow without registering everything by hand.

Run with:  python -m scripts.seed_dummy_data

Safe to re-run — skips anything that already exists by email/slot number.
"""
import io
import os
import sys
from calendar import monthrange
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.parking_slot import ParkingSlot, SlotStatus, SlotType  # noqa: E402
from app.models.payment import Payment, PaymentStatus  # noqa: E402
from app.models.payment_screenshot import PaymentScreenshot  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402

DEFAULT_PASSWORD = "Password@123"


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    """Shift (year, month) by `delta` months (can be negative)."""
    index = (year * 12 + (month - 1)) + delta
    return index // 12, (index % 12) + 1


def make_placeholder_screenshot(label: str, color: tuple[int, int, int]) -> str:
    """Creates a small placeholder JPEG so the admin screenshot viewer has
    something real to display, and returns its saved file path."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    img = Image.new("RGB", (400, 300), color=color)
    file_path = os.path.join(settings.UPLOAD_DIR, f"dummy_{label}.jpg")
    img.save(file_path, format="JPEG", quality=80)
    return file_path


def get_or_create_user(db, *, name, email, phone, room_no, role=UserRole.RESIDENT):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user, False
    user = User(
        name=name,
        email=email,
        phone=phone,
        room_no=room_no,
        password_hash=hash_password(DEFAULT_PASSWORD),
        role=role,
    )
    db.add(user)
    db.flush()
    return user, True


def get_or_create_slot(db, *, slot_number, slot_type=SlotType.RESIDENT):
    slot = db.query(ParkingSlot).filter(ParkingSlot.slot_number == slot_number).first()
    if slot:
        return slot, False
    slot = ParkingSlot(slot_number=slot_number, type=slot_type)
    db.add(slot)
    db.flush()
    return slot, True


def assign_slot(db, user: User, slot: ParkingSlot):
    slot.assigned_user_id = user.id
    slot.status = SlotStatus.ASSIGNED
    user.parking_slot_id = slot.id


def add_payment(db, user: User, slot: ParkingSlot, month: int, year: int, status: PaymentStatus,
                 with_screenshot: bool = True, rejection_reason: str | None = None, label: str = ""):
    existing = db.query(Payment).filter(
        Payment.user_id == user.id, Payment.month == month, Payment.year == year
    ).first()
    if existing:
        return existing

    now = datetime.now(timezone.utc)
    payment = Payment(
        user_id=user.id,
        parking_slot_id=slot.id if slot else None,
        amount=settings.DEFAULT_PAYMENT_AMOUNT,
        month=month,
        year=year,
        description="UPI transfer" if with_screenshot else None,
        status=status,
    )
    if status == PaymentStatus.APPROVED:
        payment.approved_at = now
    if status == PaymentStatus.REJECTED:
        payment.rejected_at = now
        payment.rejection_reason = rejection_reason or "Screenshot unclear, please resubmit."

    db.add(payment)
    db.flush()

    if with_screenshot:
        file_path = make_placeholder_screenshot(label or f"user{user.id}_{month}_{year}", (100, 150, 200))
        db.add(PaymentScreenshot(payment_id=payment.id, user_id=user.id, file_path=file_path))

    return payment


def main() -> None:
    db = SessionLocal()
    today = datetime.now(timezone.utc).date()
    cur_year, cur_month = today.year, today.month
    prev_year, prev_month = shift_month(cur_year, cur_month, -1)
    two_ago_year, two_ago_month = shift_month(cur_year, cur_month, -2)

    try:
        # --- Admin ---
        admin, created = get_or_create_user(
            db, name="Society Admin", email="admin@society.local",
            phone="9999999999", room_no="ADMIN", role=UserRole.ADMIN,
        )
        print(f"{'Created' if created else 'Exists'}: admin -> admin@society.local / {DEFAULT_PASSWORD if created else '(unchanged)'}")

        # --- Resident 1: Priya - paid this month (green) ---
        priya, c1 = get_or_create_user(db, name="Priya Sharma", email="priya@example.com", phone="9876500001", room_no="A-101")
        slot_a, _ = get_or_create_slot(db, slot_number="A-101")
        assign_slot(db, priya, slot_a)
        add_payment(db, priya, slot_a, cur_month, cur_year, PaymentStatus.APPROVED, label="priya")

        # --- Resident 2: Rahul - submitted, awaiting admin approval (orange) ---
        rahul, c2 = get_or_create_user(db, name="Rahul Verma", email="rahul@example.com", phone="9876500002", room_no="B-202")
        slot_b, _ = get_or_create_slot(db, slot_number="B-202")
        assign_slot(db, rahul, slot_b)
        add_payment(db, rahul, slot_b, cur_month, cur_year, PaymentStatus.PENDING, label="rahul")

        # --- Resident 3: Ananya - also submitted, awaiting admin approval (orange) ---
        ananya, c3 = get_or_create_user(db, name="Ananya Iyer", email="ananya@example.com", phone="9876500003", room_no="C-303")
        slot_c, _ = get_or_create_slot(db, slot_number="C-303")
        assign_slot(db, ananya, slot_c)
        add_payment(db, ananya, slot_c, cur_month, cur_year, PaymentStatus.PENDING, label="ananya")

        # --- Resident 4: Karan - never paid 2 months ago -> OVERDUE (red); this month untouched (due) ---
        karan, c4 = get_or_create_user(db, name="Karan Mehta", email="karan@example.com", phone="9876500004", room_no="D-404")
        slot_d, _ = get_or_create_slot(db, slot_number="D-404")
        assign_slot(db, karan, slot_d)
        # No payment row at all for two_ago / current -> resolves to OVERDUE / DUE automatically

        # --- Resident 5: Sneha - admin rejected this month's submission (red/rejected) ---
        sneha, c5 = get_or_create_user(db, name="Sneha Nair", email="sneha@example.com", phone="9876500005", room_no="E-505")
        slot_e, _ = get_or_create_slot(db, slot_number="E-505")
        assign_slot(db, sneha, slot_e)
        add_payment(
            db, sneha, slot_e, cur_month, cur_year, PaymentStatus.REJECTED,
            rejection_reason="Screenshot unclear, please resubmit.", label="sneha",
        )
        # Sneha also has last month approved, to show history
        add_payment(db, sneha, slot_e, prev_month, prev_year, PaymentStatus.APPROVED, label="sneha_prev")

        db.commit()

        print("\nSeed complete. All resident passwords:", DEFAULT_PASSWORD)
        print(f"Period used as 'current month': {cur_month}/{cur_year}")
        print(f"Period used as 'overdue (2 months ago)': {two_ago_month}/{two_ago_year}")
        print("\nLogin  |  Email               |  Expect to see")
        print("------ | -------------------- | ------------------------------------------")
        print("Admin  | admin@society.local  | 2 pending approvals waiting (Rahul, Ananya)")
        print("User   | priya@example.com    | This month: PAID (green)")
        print("User   | rahul@example.com    | This month: PENDING (orange)")
        print("User   | ananya@example.com   | This month: PENDING (orange)")
        print("User   | karan@example.com    | 2 months ago: OVERDUE (red); this month: DUE")
        print("User   | sneha@example.com    | This month: REJECTED; last month: PAID")

    finally:
        db.close()


if __name__ == "__main__":
    main()
