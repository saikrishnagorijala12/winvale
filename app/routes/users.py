from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.auth.dependencies import get_current_user
from app.database import get_db
import app.services.user as u
from app.utils.admin_check import require_admin
from app.utils.cache import cache_get_or_set, invalidate_keys
from app.redis_client import redis_client

router = APIRouter(prefix="/users", tags=["Users"])

CACHE_TTL = 86400


def _invalidate_user_cache(email: str):
    invalidate_keys(
        redis_client,
        "users:all",
        f"users:me:{email}",
        f"users:me:status:{email}",
        f"users:current:{email}",
    )


@router.get("/me")
def get_me(user=Depends(u.get_or_create_user)):
    return user


@router.get("/me/status")
def get_my_status(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = current_user["email"]
    return cache_get_or_set(
        redis_client,
        f"users:me:status:{email}",
        CACHE_TTL,
        lambda: u.get_user_status_by_email(db, email),
    )


@router.get("")
def get_current_user_by_email(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = current_user["email"]
    return cache_get_or_set(
        redis_client,
        f"users:current:{email}",
        CACHE_TTL,
        lambda: u.get_current_user_by_email(db, email),
    )


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = current_user["email"]
    require_admin(db, email)

    try:
        result = u.create_user_service(
            db,
            name=payload.name,
            email=str(payload.email),
            phone_no=payload.phone_no,
            role_name=payload.role_name,
        )
        invalidate_keys(redis_client, "users:all")
        return result

    except u.UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )


@router.put("", response_model=UserRead)
def update_user(
    payload: UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = str(current_user["email"])
    result = u.update_user(
        db,
        name=payload.name,
        email=email,
        phone_no=payload.phone_no,
    )
    _invalidate_user_cache(email)
    return result


@router.patch("/{user_id}/approve")
def approve_or_reject_user(
    user_id: int,
    action: str = Query(..., regex="^(approve|reject)$"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = current_user["email"]
    require_admin(db, email)

    try:
        if action == "approve":
            u.approve_user_service(db, user_id=user_id)
            invalidate_keys(redis_client, "users:all")
            return {"message": "User approved"}

        if action == "reject":
            u.reject_user_service(db, user_id=user_id)
            invalidate_keys(redis_client, "users:all")
            return {"message": "User rejected"}

    except u.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.get("/all")
def get_all_users(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not require_admin(db, current_user["email"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return cache_get_or_set(
        redis_client, "users:all", CACHE_TTL, lambda: u.get_all_users(db)
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(db, current_user["email"])
    result = u.delete_user(db, user_id)
    invalidate_keys(redis_client, "users:all")
    return result


@router.put("/change_role/{user_id}")
def change_role(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(db, current_user["email"])
    result = u.change_user_role(db, user_id, current_user["email"])
    invalidate_keys(redis_client, "users:all")
    return result
