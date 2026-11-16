import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User, RoleEnum


def seed_roles():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users_to_seed = [
            ("admin", "admin@textilewaste.platform", "AdminSecret2026!", RoleEnum.ADMIN),
            ("operator1", "operator@textilewaste.platform", "OperatorSecret2026!", RoleEnum.OPERATOR),
            ("sustain1", "sustain@textilewaste.platform", "SustainSecret2026!", RoleEnum.SUSTAINABILITY_MANAGER),
            ("manuf1", "manuf@textilewaste.platform", "ManufSecret2026!", RoleEnum.MANUFACTURER),
        ]

        for username, email, pwd, role in users_to_seed:
            existing = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            if existing:
                existing.role = role
                existing.hashed_password = get_password_hash(pwd)
                existing.is_active = True
                print(f"[seed] Updated user '{username}' with role '{role.value}'")
            else:
                user = User(
                    username=username,
                    email=email,
                    hashed_password=get_password_hash(pwd),
                    role=role,
                    is_active=True
                )
                db.add(user)
                print(f"[seed] Created user '{username}' with role '{role.value}'")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()
