import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User, RoleEnum


def seed_admin(
    username: str = "admin",
    email: str = "admin@textilewaste.platform",
    password: str = "AdminSecret2026!"
):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing:
            print(f"[seed] Admin user '{username}' already exists. Updating credentials.")
            existing.hashed_password = get_password_hash(password)
            existing.role = RoleEnum.ADMIN
            existing.is_active = True
            db.commit()
            print("[seed] Admin updated successfully.")
            return

        admin_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role=RoleEnum.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print(f"[seed] Initial administrator '{username}' created successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
