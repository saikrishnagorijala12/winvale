from sqlalchemy.orm import Session
from fastapi import Depends
from app.models.users import User
from datetime import datetime, timezone
from app.auth.dependencies import get_current_user
from app.database import get_db


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
        "Role":user.role_id
    }


def replace_user_by_email(db: Session, *, name: str, email: str, phone_no: str, role_id: int):
    """
    FULL replacement of user data.
    PUT semantics.
    """

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {
            "Response Type": "Error",
            "Message": "User Not Found"
        }

    user.name = name
    user.email = email
    user.phone_no = phone_no
    user.role_id = role_id
   
    db.commit()
    db.refresh(user)

    return user



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

DEFAULT_ROLE_ID = 2 

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
            phone_no="NA",
            role_id=DEFAULT_ROLE_ID,
            is_active=False,
            cognito_sub=token_user["sub"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user