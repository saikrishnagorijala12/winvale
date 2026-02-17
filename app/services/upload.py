from io import BytesIO
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.models.product_master import ProductMaster
from app.models.product_history import ProductHistory
from app.models.product_dim import ProductDim
from app.models.file_uploads import FileUpload
from app.utils import s3_upload as s3
from fastapi import HTTPException, status

from app.utils.upload_helper import (
    MASTER_FIELDS,
    HISTORY_FIELDS,
    DIM_FIELDS,
    normalize,
    identity_signature,
    history_signature,
)


def upload_products(db: Session, client_id: int, file, user_email: str):

    if not db.query(ClientProfile).filter_by(client_id=client_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client Not Found"
        )

    if not db.query(ClientContracts).filter_by(client_id=client_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Contract Found for Selected Client"
        )


    raw = pd.read_excel(BytesIO(file.file.read()), header=None)
    raw = raw.drop(index=0).reset_index(drop=True)
    raw.columns = raw.iloc[0]
    df = raw.drop(index=0).reset_index(drop=True)

    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

    inserted = updated = skipped = 0

    for _, row in df.iterrows():

        row_data = {
            col: normalize(row.get(col), col)
            for col in df.columns
        }

        manufacturer = row_data.get("manufacturer")
        mpn = row_data.get("manufacturer_part_number")

        if not manufacturer or not mpn:
            skipped += 1
            continue

        identity_sig = identity_signature(row_data)
        history_sig = history_signature(row_data)

        product = (
            db.query(ProductMaster)
            .filter_by(
                client_id=client_id,
                manufacturer=manufacturer,
                manufacturer_part_number=mpn,
            )
            .first()
        )

        if not product:

            master_payload = {
                f: row_data.get(f)
                for f in MASTER_FIELDS
                if row_data.get(f) is not None
            }

            product = ProductMaster(
                client_id=client_id,
                row_signature=identity_sig,
                **master_payload,
            )

            db.add(product)
            db.flush()

            history_payload = {
                f: row_data.get(f)
                for f in HISTORY_FIELDS
                if row_data.get(f) is not None
            }
            history_payload["currency"] = history_payload.get("currency") or "USD"

            db.add(
                ProductHistory(
                    product_id=product.product_id,
                    client_id=client_id,
                    row_signature=history_sig,
                    is_current=True,
                    **history_payload,
                )
            )

            dim_payload = {
                f: row_data.get(f)
                for f in DIM_FIELDS
                if row_data.get(f) is not None
            }

            db.add(
                ProductDim(
                    product_id=product.product_id,
                    **dim_payload,
                )
            )

            inserted += 1
            continue

        # ---------------- UPDATE ----------------
        current = (
            db.query(ProductHistory)
            .filter_by(product_id=product.product_id, is_current=True)
            .first()
        )

        if current and current.row_signature == history_sig:
            skipped += 1
            continue

        if current:
            current.is_current = False
            current.effective_end_date = datetime.utcnow()

        history_payload = {
            f: row_data.get(f)
            for f in HISTORY_FIELDS
            if row_data.get(f) is not None
        }
        history_payload["currency"] = history_payload.get("currency") or "USD"

        db.add(
            ProductHistory(
                product_id=product.product_id,
                client_id=client_id,
                row_signature=history_sig,
                is_current=True,
                **history_payload,
            )
        )

        for f in MASTER_FIELDS:
            value = row_data.get(f)
            if value is not None:
                setattr(product, f, value)

        product.row_signature = identity_sig

        dim = product.dimension
        if not dim:
            dim_payload = {
                f: row_data.get(f)
                for f in DIM_FIELDS
                if row_data.get(f) is not None
            }
            db.add(ProductDim(product_id=product.product_id, **dim_payload))
        else:
            for f in DIM_FIELDS:
                value = row_data.get(f)
                if value is not None:
                    setattr(dim, f, value)

        updated += 1

    db.commit()

    
    if inserted or updated:
        s3.save_uploaded_file(db, client_id, file, user_email, "gsa_upload")
        return {
            "status_code": status.HTTP_201_CREATED,
            "message": "File inserted or updated successfully",
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "update_status": bool(inserted or updated),
        }

    return {
        "status_code": status.HTTP_200_OK,
        "message": "No changes made",
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "update_status": bool(inserted or updated),
    }