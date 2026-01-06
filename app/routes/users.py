from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.user import UserCreate, UserRead
from app.auth.dependencies import get_current_user
from app.database import get_db
import app.services.user as u

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me/status")
def get_my_status(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = current_user["email"]

    return u.get_user_status_by_email(db, email)

@router.get("")
def get_user_current(
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
    # if payload.email != current_user["email"]:
    if current_user["email"] != "gujjasreya2000@gmail.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin Needed"
        )

    try:
        return u.create_user_service(
            db,
            name=payload.name,
            email=payload.email,
            phone_no=payload.phone_no,
            role_id=payload.role_id,
        )

    except u.UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
@router.put("", response_model=UserRead)
def replace_current_user(
    payload: UserCreate,   
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    email = current_user["email"]

    return u.replace_user_by_email(db, email, payload)




@router.patch("/{user_id}/approve")
def approve_user(
    user_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if "admin" not in current_user.get("groups", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only"
        )

    try:
        u.approve_user_service(db, user_id=user_id)
        return {"message": "User approved"}

    except u.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
