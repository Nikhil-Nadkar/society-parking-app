import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"       # submitted, waiting for admin (orange)
    APPROVED = "approved"     # paid (green)
    REJECTED = "rejected"     # rejected (red/needs resubmit)
    OVERDUE = "overdue"       # nothing submitted, past grace period (red)
    NOT_DUE = "not_due"       # future / not required yet


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        # A user can only have ONE *active* (pending/approved) payment per month/year.
        # Rejected/overdue rows don't block a new submission, enforced in the service layer
        # since MySQL unique constraints can't easily be partial; we still index for lookups.
        UniqueConstraint("user_id", "month", "year", "status", name="uq_user_month_year_status"),
        Index("ix_payment_user_period", "user_id", "year", "month"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parking_slot_id: Mapped[int | None] = mapped_column(
        ForeignKey("parking_slots.id", ondelete="SET NULL"), nullable=True
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    year: Mapped[int] = mapped_column(Integer, nullable=False)   # e.g. 2027
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user = relationship("User", back_populates="payments", foreign_keys=[user_id])
    parking_slot = relationship("ParkingSlot", foreign_keys=[parking_slot_id])
    approver = relationship("User", foreign_keys=[approved_by])
    screenshots = relationship("PaymentScreenshot", back_populates="payment", cascade="all, delete-orphan")
