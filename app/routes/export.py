from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.services.export import export_products_excel, export_price_modifications_excel, get_master_filename
from io import BytesIO
from typing import List, Optional
from fastapi import Query
from datetime import datetime, timezone

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/price-modifications")
def export_price_modifications(
    client_id: Optional[int] = Query(None),
    job_id: Optional[int] = Query(None),
    types: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
):
    wb = export_price_modifications_excel(
        db=db,
        client_id=client_id,
        job_id=job_id,
        selected_types=types,
    )

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"price_modifications_{date_str}.xlsx"

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/")
def export_products(
    client_id: Optional[int] = Query(None),
    # current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wb = export_products_excel(db, client_id)

    filename = get_master_filename(db, client_id)

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


# @router.get("/{client_id}")
# def export_products(
#     client_id:int,
#     current_user=Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     wb = export_products_excel(db,client_id)

#     filename=get_master_filename(db,client_id)

#     stream = BytesIO()
#     wb.save(stream)
#     stream.seek(0)

#     return StreamingResponse(
#         stream,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={
#             "Content-Disposition": f'attachment; filename="{filename}"'
#         },
#     )