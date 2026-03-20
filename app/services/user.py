from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.models.users import User
from datetime import datetime, timezone
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.utils.name_to_id import get_role_id_by_name, get_status_id_by_name
from app.schemas.user import UserStatusRead, UserAuthRead, UserListRead, UserRead


def serialize_user(user: User, message: str | None = None) -> UserRead:
    return UserRead.model_validate({
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone_no": user.phone_no,
        "is_active": user.is_active,
        "is_deleted": user.is_deleted,
        "role": user.role.role_name,
        "created_time": user.created_time,
        "message": message
    })


def get_user_status_by_email(db: Session, email: str) -> UserStatusRead:
    """
    Business logic only.
    No FastAPI, no Depends, no HTTP.
    """

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return UserStatusRead.model_validate({
            "registered": False,
            "is_active": False
        })

    return UserStatusRead.model_validate({

        "registered": True,
        "is_active": user.is_active,
        "Role": user.role.role_name
    })


def get_current_user_by_email(db: Session, email: str) -> UserRead:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    return serialize_user(user, message="User Feched sucessfully")


def update_user(
    db: Session,
    *,
    name: str,
    email: str,
    phone_no: str | None = None,
):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if phone_no is not None:
        existing = (
            db.query(User)
            .filter(
                User.phone_no == phone_no,
                User.user_id != user.user_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Phone Number Already Exists"
            )

    user.name = name
    user.phone_no = phone_no

    db.commit()
    db.refresh(user)

    return serialize_user(user, message="User Details updated successfully")


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


    return serialize_user(user, message="User Created sucessfully")



class UserNotFoundError(Exception):
    pass


def approve_user_service(db: Session, *, user_id: int) -> UserRead:
    user = db.query(User).filter(User.user_id == user_id).first()
 
    if not user:
        raise UserNotFoundError()
 
    if user.is_active:
        return serialize_user(user)
    
    # if not user.is_deleted:
    #     return user
 
    user.is_active = True
    user.is_deleted = False
    db.commit()
    db.refresh(user)


    return serialize_user(user, message="User Approved sucessfully")



def reject_user_service(db: Session, *, user_id: int) -> UserRead:
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

    return serialize_user(user, message="User Rejected sucessfully")


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

    return serialize_user(user, message="User Created/updated sucessfully")


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    search: str | None = None
) -> dict:
    from sqlalchemy import or_
    query = db.query(User)

    if status and status != "all":
        if status == "pending":
            query = query.filter(User.is_active.is_(False), User.is_deleted.is_(False))
        elif status == "approved":
            query = query.filter(User.is_active.is_(True), User.is_deleted.is_(False))
        elif status == "rejected":
            query = query.filter(User.is_deleted.is_(True))

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    total_count = query.count()
    users = query.order_by(User.created_time.desc()).offset(skip).limit(limit).all()
    
    user_list = [
        {
            "user_id": u.user_id,
            "name": u.name,
            "email": u.email,
            "phone_no": u.phone_no,
            "is_active": u.is_active,
            "is_deleted": u.is_deleted,
            "role": u.role.role_name,
            "created_time" : u.created_time
        }
        for u in users
    ]
    return {
        "users": user_list,
        "total_count": total_count,
        "status_counts": {
            "all": db.query(User).count(),
            "pending": db.query(User).filter(User.is_active.is_(False), User.is_deleted.is_(False)).count(),
            "approved": db.query(User).filter(User.is_active.is_(True), User.is_deleted.is_(False)).count(),
            "rejected": db.query(User).filter(User.is_deleted.is_(True)).count(),
        }
    }

def delete_user(db: Session, user_id:int) -> UserRead:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise UserNotFoundError()

    if user.is_deleted:
        return serialize_user(user)

    user.is_deleted = True
    user.is_active = False
    db.commit()
    db.refresh(user)

    return serialize_user(user, message="User Deactivated sucessfully")


def change_user_role(db: Session, user_id:int,email:str) -> UserRead:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise UserNotFoundError()
    
    if user.email == email:
        raise HTTPException(status_code=403, detail="Action Not Allowed for this User")

    if user.is_deleted:
        raise HTTPException(status_code=400, detail="User is deleted")
    
    if user.role_id == 1:
        user.role_id = 2
        db.commit()
        db.refresh(user)
    elif user.role_id == 2:
        user.role_id = 1
        db.commit()
        db.refresh(user)

    return serialize_user(user, message="User role changed sucessfully")