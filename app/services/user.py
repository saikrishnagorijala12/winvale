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
    
    message = "User Feched sucessfully",

    return {
        "user_id" : user.user_id,
        "name" : user.name,
        "email" : user.email,
        "phone_no" : user.phone_no,
        "is_active" : user.is_active,
        "is_deleted" : user.is_deleted,
        "role": user.role.role_name,
        "message" : message
    }


def update_user(
    db: Session,
    *,
    name: str,
    email: str ,
    phone_no: str| None = None,
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    user.name = name
    if phone_no is not None:
        user.phone_no = phone_no

    db.commit()
    db.refresh(user)

    message = "User Details updated sucessfully",

    return {
        "user_id" : user.user_id,
        "name" : user.name,
        "email" : user.email,
        "phone_no" : user.phone_no,
        "is_active" : user.is_active,
        "is_deleted" : user.is_deleted,
        "role": user.role.role_name,
        "message" : message
    }




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


    message = "User Created sucessfully",

    return {
        "user_id" : user.user_id,
        "name" : user.name,
        "email" : user.email,
        "phone_no" : user.phone_no,
        "is_active" : user.is_active,
        "is_deleted" : user.is_deleted,
        "role": user.role.role_name,
        "message" : message
    }



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


    message = "User Approved sucessfully",


    return {
        "user_id" : user.user_id,
        "name" : user.name,
        "email" : user.email,
        "phone_no" : user.phone_no,
        "is_active" : user.is_active,
        "is_deleted" : user.is_deleted,
        "role": user.role.role_name,
        "message" : message
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

    message = "User Rejected sucessfully",
 
    return {
        "user_id" : user.user_id,
        "name" : user.name,
        "email" : user.email,
        "phone_no" : user.phone_no,
        "is_active" : user.is_active,
        "is_deleted" : user.is_deleted,
        "role": user.role.role_name,
        "message" : message
    }


DEFAULT_ROLE_NAME = "user"

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
            role_id = get_role_id_by_name(db, DEFAULT_ROLE_NAME),
            is_active=False,
            cognito_sub=token_user["sub"]
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    message ="User Created/updated sucessfully"

 
    return {
        "user_id" : user.user_id,
        "name" : user.name,
        "email" : user.email,
        "phone_no" : user.phone_no,
        "is_active" : user.is_active,
        "is_deleted" : user.is_deleted,
        "role": user.role.role_name,
        "message" : message
    }


def get_all_users(db: Session):
    users = db.query(User).all()
    return [
        {
            "user_id": u.user_id,
            "name": u.name,
            "email": u.email,
            "phone_no": u.phone_no,
            "is_active": u.is_active,
            "is_deleted": u.is_deleted,
            "role": u.role.role_name,
        }
        for u in users
    ]

def delete_user(db: Session, user_id:int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise UserNotFoundError()

    if user.is_deleted:
        return user

    user.is_deleted = True
    db.commit()
    db.refresh(user)

    message = "User Deactivated sucessfully",

    return {
        "user_id" : user.user_id,
        "name" : user.name,
        "email" : user.email,
        "phone_no" : user.phone_no,
        "is_active" : user.is_active,
        "is_deleted" : user.is_deleted,
        "role": user.role.role_name,
        "message" : message
    }

