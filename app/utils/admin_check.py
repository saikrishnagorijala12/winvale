# app/services/authz.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.users import User

ADMIN_ROLE_ID = 2


def get_db_user_by_email(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def require_admin(db: Session, email: str) -> User:
    user = get_db_user_by_email(db, email)

    if user.role_id != ADMIN_ROLE_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only"
        )

    return user
