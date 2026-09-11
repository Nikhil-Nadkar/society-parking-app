import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SlotType(str, enum.Enum):
    RESIDENT = "resident"
    GUEST = "guest"
    DELIVERY = "delivery"


class SlotStatus(str, enum.Enum):
    UNUSED = "unused"
    ASSIGNED = "assigned"


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slot_number: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    type: Mapped[SlotType] = mapped_column(
        Enum(SlotType), default=SlotType.RESIDENT, nullable=False
    )
    status: Mapped[SlotStatus] = mapped_column(
        Enum(SlotStatus), default=SlotStatus.UNUSED, nullable=False
    )

    # Denormalized pointer kept in sync with users.parking_slot_id via the API layer.
    assigned_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # assigned_user = relationship("User", back_populates="parking_slot", foreign_keys=[assigned_user_id])
    assigned_user = relationship("User", foreign_keys=[assigned_user_id], uselist=False)
