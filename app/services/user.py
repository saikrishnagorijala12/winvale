from sqlalchemy.orm import Session
from fastapi import Depends
from app.models.users import User
from datetime import datetime, timezone
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.utils.name_to_id import get_role_id_by_name, get_status_id_by_name


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
        "Role": user.role.role_name
    }


def get_current_user_by_email(db: Session, email: str):
    """
    Business logic only.
    No FastAPI, no Depends, no HTTP.
    """

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {
            "Response Type": "Error",
            "Message": "User Not Found"
        }

    return {
        
        "Full Name" : user.name,
        "Email Address" : user.email,
        "Contact Number" : user.phone_no,
        "Active Status" : user.is_active,
        "Role": user.role.role_name
    }


def update_user(
    db: Session,
    *,
    name: str,
    email: str,
    phone_no: str,
    role_name: str,
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    user.name = name
    user.phone_no = phone_no
    user.role_id = get_role_id_by_name(db, role_name)

    db.commit()
    db.refresh(user)

    return user



class UserAlreadyExistsError(Exception):
    pass


def create_user_service(
    db: Session,
    *,
    name: str,
    email: str,
    phone_no: str,
    role_name: str,
):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise UserAlreadyExistsError()

    role_id = get_role_id_by_name(db, role_name)

    user = User(
        name=name,
        email=email,
        phone_no=phone_no,
        role_id=role_id,
        is_active=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


class UserNotFoundError(Exception):
    pass


def approve_user_service(db: Session, *, user_id: int) -> User:
    user = db.query(User).filter(User.user_id == user_id).first()
 
    if not user:
        raise UserNotFoundError()
 
    if user.is_active:
        return user
 
    user.is_active = True
    db.commit()
    db.refresh(user)
 
    return {
        "user_id" : user.user_id,
        "phone_no" : user.phone_no,
        "email" : user.email,
        "role":user.role.role_name,
        "is_active": user.is_active,
        "is_deleted":user.is_deleted
    }


def reject_user_service(db: Session, *, user_id: int) -> User:
    user = (
        db.query(User)
        .filter(
            User.user_id == user_id,
            User.is_deleted.is_(False),
        )
        .first()
    )
 
    if not user:
        raise UserNotFoundError()
 
    user.is_deleted = True
    user.is_active = False
 
    db.commit()
    db.refresh(user)
 
    return {
        "user_id" : user.user_id,
        "phone_no" : user.phone_no,
        "email" : user.email,
        "role":user.role.role_name,
        "is_active": user.is_active,
        "is_deleted":user.is_deleted
    }

DEFAULT_ROLE_NAME = "admin"

def get_or_create_user(
    token_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.cognito_sub == token_user["sub"]
    ).first()

    if not user:
        user = User(
            name=token_user["name"],
            email=token_user["email"],
            phone_no=None,
            role_name = get_role_id_by_name(db, DEFAULT_ROLE_NAME),
            is_active=False,
            cognito_sub=token_user["sub"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "user_id" : user.user_id,
        "phone_no" : user.phone_no,
        "email" : user.email,
        "role":user.role.role_name,
        "is_active": user.is_active,
        "is_deleted":user.is_deleted
    }

def get_all_users(db: Session):
    return db.query(User).all()

def delete_user(db: Session, user_id:int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise UserNotFoundError()

    if user.is_deleted:
        return user

    user.is_deleted = True
    db.commit()
    db.refresh(user)

    return user

