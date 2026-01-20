from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.services.export import export_products_excel,get_master_filename
from io import BytesIO

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/{client_id}")
def export_products(
    client_id:int,
    # current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wb = export_products_excel(db,client_id)

    filename=get_master_filename(db,client_id)

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