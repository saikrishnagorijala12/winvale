from io import BytesIO
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy.orm import Session

from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.models.product_master import ProductMaster
from app.models.product_history import ProductHistory
from app.models.product_dim import ProductDim
from app.models.users import User
from app.models.file_uploads import FileUpload
from app.utils import upload as s3

import re
import os

from app.utils.upload_helper import (
    MASTER_FIELDS,
    HISTORY_FIELDS,
    DIM_FIELDS,
    normalize,
    identity_signature,
    history_signature,
)


def upload_products(db: Session, client_id: int, file, user_email: str):

    # -------------------------
    # Guard rails
    # -------------------------
    if not db.query(ClientProfile).filter_by(client_id=client_id).first():
        raise ValueError("Invalid client")

    if not db.query(ClientContracts).filter_by(client_id=client_id).first():
        raise ValueError("Invalid contract")

    # -------------------------
    # Read Excel
    # -------------------------
    raw = pd.read_excel(BytesIO(file.file.read()), header=None)
    raw = raw.drop(index=0).reset_index(drop=True)
    raw.columns = raw.iloc[0]
    df = raw.drop(index=0).reset_index(drop=True)

    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

    inserted = updated = skipped = 0

    # -------------------------
    # Process rows
    # -------------------------
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

        # =================================================
        # INSERT
        # =================================================
        if not product:
            product = ProductMaster(
                client_id=client_id,
                row_signature=identity_sig,
                **{f: row_data.get(f) for f in MASTER_FIELDS},
            )
            db.add(product)
            db.flush()

            history_payload = {
                f: row_data.get(f)
                for f in HISTORY_FIELDS
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

            db.add(
                ProductDim(
                    product_id=product.product_id,
                    **{f: row_data.get(f) for f in DIM_FIELDS},
                )
            )

            inserted += 1
            continue

        # =================================================
        # UPDATE
        # =================================================
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
            setattr(product, f, row_data.get(f))

        product.row_signature = identity_sig

        dim = product.dimension
        if not dim:
            db.add(
                ProductDim(
                    product_id=product.product_id,
                    **{f: row_data.get(f) for f in DIM_FIELDS},
                )
            )
        else:
            for f in DIM_FIELDS:
                setattr(dim, f, row_data.get(f))

        updated += 1

    db.commit()

    if inserted or updated:
        save_uploaded_file(db, client_id, file, user_email)

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "update_status": bool(inserted or updated),
    }

def clean(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", value.strip())


def save_uploaded_file(db: Session, client_id: int, file, user_email: str):
    client = db.query(ClientProfile).filter_by(client_id=client_id).first()
    user = db.query(User).filter_by(email=user_email).first()

    _, ext = os.path.splitext(file.filename)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    filename = (
        f"{clean(client.company_name)}_"
        f"{date_str}_"
        f"{clean(user.name)}"
        f"{ext}"
    )

    result = s3.gsa_upload(file, filename)

    db.add(
        FileUpload(
            user_id=user.user_id,
            uploaded_by=user.user_id,
            client_id=client_id,
            original_filename=file.filename,
            s3_saved_filename=filename,
            s3_saved_path=result["url"],
            file_size=result["size"],
        )
    )

    db.commit()
    return result
