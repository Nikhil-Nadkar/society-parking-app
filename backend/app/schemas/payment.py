from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2020, le=2100)
    description: str | None = Field(default=None, max_length=500)


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    amount: float
    month: int
    year: int
    description: str | None
    status: PaymentStatus
    created_at: datetime
    approved_at: datetime | None
    rejected_at: datetime | None
    rejection_reason: str | None


class PaymentMonthStatus(BaseModel):
    month: int
    year: int
    status: str  # one of: approved, pending, overdue, rejected, due, not_due
    payment_id: int | None = None


class PaymentApprove(BaseModel):
    pass


class PaymentReject(BaseModel):
    rejection_reason: str | None = Field(default=None, max_length=500)


class PaymentAdminOut(PaymentOut):
    user_name: str
    room_no: str
    slot_number: str | None = None
