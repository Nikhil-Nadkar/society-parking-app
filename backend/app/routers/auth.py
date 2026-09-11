from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_reset_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.parking_slot import ParkingSlot, SlotStatus
from app.models.user import User
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLogin,
    UserOut,
    UserRegister,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    slot = None
    if payload.parking_no:
        slot = db.query(ParkingSlot).filter(ParkingSlot.slot_number == payload.parking_no).first()
        if slot is None:
            slot = ParkingSlot(slot_number=payload.parking_no)
            db.add(slot)
            db.flush()
        elif slot.assigned_user_id is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parking slot already assigned.")

    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        room_no=payload.room_no,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()

    if slot is not None:
        slot.assigned_user_id = user.id
        slot.status = SlotStatus.ASSIGNED
        user.parking_slot_id = slot.id

    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    # Always return a generic response to avoid leaking which emails are registered.
    if user is None:
        return {"message": "If that email is registered, a reset link has been generated."}

    reset_token = create_reset_token(user.id)
    # In production this would be emailed. For local dev/MVP we return it directly.
    return {"message": "Reset token generated.", "reset_token": reset_token}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    claims = decode_token(payload.token)
    if claims is None or claims.get("type") != "reset":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")

    user = db.get(User, int(claims["sub"]))
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password reset successfully."}
