"""Run with: python -m scripts.seed_admin
Creates (or promotes) an admin user for local development/testing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402

ADMIN_EMAIL = "admin@society.local"
ADMIN_PASSWORD = "Admin@12345"


def main() -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if user:
            user.role = UserRole.ADMIN
            print(f"Promoted existing user {ADMIN_EMAIL} to admin.")
        else:
            user = User(
                name="Society Admin",
                email=ADMIN_EMAIL,
                phone="9999999999",
                room_no="ADMIN",
                password_hash=hash_password(ADMIN_PASSWORD),
                role=UserRole.ADMIN,
            )
            db.add(user)
            print(f"Created admin user {ADMIN_EMAIL} / password: {ADMIN_PASSWORD}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
