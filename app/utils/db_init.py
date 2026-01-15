from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.status import Status


def seed_static_data(db: Session):
    """
    Seed non-changing data like roles and statuses.
    Safe to run multiple times.
    """
    roles = [
        "admin",
        "user",
        "manager"
    ]

    for role_name in roles:
        exists = db.query(Role).filter_by(role_name=role_name).first()
        if not exists:
            db.add(Role(role_name=role_name))

    # --- Status ---
    statuses = [
        "pending",
        "active",
        "inactive",
        "aproved",
        "rejected",
        "Unknown"
    ]

    for status_code in statuses:
        exists = db.query(Status).filter_by(status_code=status_code).first()
        if not exists:
            db.add(Status(status_code=status_code))

    db.commit()
    db.close()