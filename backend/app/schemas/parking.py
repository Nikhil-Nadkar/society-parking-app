from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.parking_slot import SlotStatus, SlotType


class ParkingSlotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slot_number: str
    type: SlotType
    status: SlotStatus
    assigned_user_id: int | None


class ParkingSlotWithPaymentStatus(ParkingSlotOut):
    payment_status: str | None = None  # current-month status: paid/overdue/pending/unused
    resident_name: str | None = None


class ParkingSlotCreate(BaseModel):
    slot_number: str = Field(max_length=20)
    type: SlotType = SlotType.RESIDENT


class ParkingSlotAssign(BaseModel):
    user_id: int | None = None  # None to unassign


class ParkingSlotUpdate(BaseModel):
    type: SlotType | None = None
    status: SlotStatus | None = None
