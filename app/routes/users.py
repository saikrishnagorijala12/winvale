from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.auth.dependencies import get_current_user
from app.database import get_db
import app.services.user as u
from app.utils.admin_check import require_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def get_me(user=Depends(u.get_or_create_user)):
    return user

@router.get("/me/status")
def get_my_status(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = current_user["email"]

    return u.get_user_status_by_email(db, email)

@router.get("")
def get_current_user_by_email(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = current_user["email"]

    return u.get_current_user_by_email(db, email)



@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = current_user["email"]
    require_admin(db, email)

    try:
        return u.create_user_service(
            db,
            name=payload.name,
            email=str(payload.email),
            phone_no=payload.phone_no,
            role_name=payload.role_name,
        )

    except u.UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
@router.put("", response_model=UserRead)
def update_user(
    payload: UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = str(current_user["email"])

    return u.update_user(
        db,
        name=payload.name,
        email=email,
        phone_no=payload.phone_no,
    )

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
            return {"message": "User approved"}
 
        if action == "reject":
            u.reject_user_service(db, user_id=user_id)
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
 
    return u.get_all_users(db)


@router.delete("/{user_id}")
def delete_user(
    user_id : int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(db, current_user["email"])
    return u.delete_user(db, user_id)

@router.put("/change_role/{user_id}")
def change_role(
    user_id:int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_admin(db, current_user["email"])
    return u.change_user_role(db,user_id,current_user["email"])
