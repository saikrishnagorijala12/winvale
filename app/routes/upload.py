from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.auth.dependencies import get_current_user
from app.services.upload import upload_products as upload_products_service

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/{client_id}", status_code=status.HTTP_202_ACCEPTED)
def upload_products(
    client_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user=Depends(get_current_user),
):
    if not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only Excel (.xlsx) files are allowed",
        )

    background_tasks.add_task(
        run_upload_background,
        client_id,
        file,
        current_user["email"],
    )

    return {
        "status": "processing",
        "message": "Upload started"
    }


def run_upload_background(client_id: int, file: UploadFile, user_email: str):
    db = SessionLocal()
    try:
        upload_products_service(
            db=db,
            client_id=client_id,
            file=file,
            user_email=user_email,
        )
    finally:
        db.close()



# from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.auth.dependencies import get_current_user
# from app.services.upload import upload_products as upload_products_service
# from app.utils.cache import invalidate_pattern
# from app.redis_client import redis_client

# router = APIRouter(prefix="/upload", tags=["Upload"])


# @router.post("/{client_id}", status_code=status.HTTP_201_CREATED)
# def upload_products(
#     client_id: int,
#     file: UploadFile = File(...),
#     current_user=Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     if not file.filename.lower().endswith(".xlsx"):
#         raise HTTPException(
#             status_code=400,
#             detail="Only Excel (.xlsx) files are allowed",
#         )

#     result = upload_products_service(
#         db=db,
#         client_id=client_id,
#         file=file,
#         user_email=current_user["email"],
#     )

#     invalidate_pattern(redis_client, "products:all*")
#     invalidate_pattern(redis_client, f"products:client:{client_id}*")

#     return result
