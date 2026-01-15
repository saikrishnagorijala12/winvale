from fastapi import HTTPException, status
from sqlalchemy.orm import Session
 
from app.models.users import User
from app.models.role import Role  
 
 
def get_db_user_by_email(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user
 
 
def get_admin_role(db: Session) -> Role:
    role = (
        db.query(Role)
        .filter(Role.role_name == "admin")
        .first()
    )
 
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin role not configured",
        )
 
    return role
 
 
def require_admin(db: Session, email: str) -> User:
    user = get_db_user_by_email(db, email)
    admin_role = get_admin_role(db)
 
    if user.role_id != admin_role.role_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only",
        )
 
    return user
 
 