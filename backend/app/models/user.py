import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    RESIDENT = "resident"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    room_no: Mapped[str] = mapped_column(String(20), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.RESIDENT, nullable=False
    )

    parking_slot_id: Mapped[int | None] = mapped_column(
        ForeignKey("parking_slots.id", ondelete="SET NULL"), nullable=True, unique=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # parking_slot = relationship("ParkingSlot", back_populates="assigned_user", foreign_keys=[parking_slot_id])
    parking_slot = relationship(
        "ParkingSlot", foreign_keys=[parking_slot_id], uselist=False
    )
    payments = relationship(
        "Payment", back_populates="user", foreign_keys="Payment.user_id"
    )
