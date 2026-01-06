from sqlalchemy.orm import Session
from app.models.users import User


def get_user_status_by_email(db: Session, email: str):
    """
    Business logic only.
    No FastAPI, no Depends, no HTTP.
    """

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {
            "registered": False,
            "is_active": False
        }

    return {
        "registered": True,
        "is_active": user.is_active,
        "role_id": user.role_id
    }


class UserAlreadyExistsError(Exception):
    pass


def create_user_service(db: Session, *, name: str, email: str, phone_no: str, role_id: int):
    """
    Creates a new user in inactive state.
    Raises domain errors, NOT HTTP errors.
    """

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise UserAlreadyExistsError()

    user = User(
        name=name,
        email=email,
        phone_no=phone_no,
        role_id=role_id,
        is_active=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


class UserNotFoundError(Exception):
    pass


def approve_user_service(db: Session, *, user_id: int):
    """
    Activates a user account.
    Assumes caller is already authorized.
    """

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise UserNotFoundError()

    if user.is_active:
        return user

    user.is_active = True
    db.commit()
    db.refresh(user)

    return user