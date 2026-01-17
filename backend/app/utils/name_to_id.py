from app.models.role import Role
from app.models.status import Status
from sqlalchemy.orm import Session

from sqlalchemy import func

def get_role_id_by_name(db: Session, role_name: str) -> int:
    role = (
        db.query(Role)
        .filter(func.lower(Role.role_name) == role_name.lower())
        .first()
    )
    if not role:
        raise ValueError("Invalid role name")
    return role.role_id


def get_status_id_by_name(db: Session, status_code: str) -> int:
    status = (
        db.query(Status)
        .filter(func.lower(Status.status_code) == status_code.lower())
        .first()
    )
    if not status:
        raise ValueError("Invalid status code")
    return status.status_id


# def get_role_id_by_name(db: Session, role_name: str) -> int:
#     role = db.query(Role).filter(str(Role.role_name).lower() == str(role_name).lower()).first()
#     if not role:
#         raise ValueError("Invalid role name")
#     return role.role_id

# def get_status_id_by_name(db: Session, status_code: str) -> int:
#     status = db.query(Role).filter(str(Status.status_code).lower() == str(status_code).lower()).first()
#     if not status:
#         raise ValueError("Invalid Status Code")
#     return status.status_id
