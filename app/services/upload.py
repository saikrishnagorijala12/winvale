from datetime import datetime
from openpyxl import load_workbook
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts
from app.models.product_master import ProductMaster
from app.models.product_history import ProductHistory
from app.models.product_dim import ProductDim
from app.utils.upload_helper import (
    MASTER_FIELDS,
    HISTORY_FIELDS,
    DIM_FIELDS,
    normalize,
    identity_signature,
    history_signature,
)
from app.redis_client import redis_client
from app.utils import s3_upload as s3


BATCH_SIZE = 1000


def upload_products(db: Session, client_id: int, file, user_email: str):

    # ----------------------------
    # Validate client
    # ----------------------------
    if not db.query(ClientProfile).filter_by(client_id=client_id).first():
        raise HTTPException(status_code=404, detail="Client Not Found")

    if not db.query(ClientContracts).filter_by(client_id=client_id).first():
        raise HTTPException(status_code=404, detail="No Contract Found")

    # ----------------------------
    # Load Excel in STREAM mode
    # ----------------------------
    file.file.seek(0)
    wb = load_workbook(file.file, read_only=True)
    sheet = wb.active

    rows = sheet.iter_rows(values_only=True)

    # Skip first 2 header rows
    next(rows)
    headers = [h for h in next(rows)]

    inserted = 0
    updated = 0
    skipped = 0

    # ----------------------------
    # Preload existing products
    # ----------------------------
    existing_products = {
        (p.manufacturer, p.manufacturer_part_number): p
        for p in db.query(ProductMaster)
        .filter_by(client_id=client_id)
        .all()
    }

    # ----------------------------
    # Preload current histories
    # ----------------------------
    current_histories = {
        h.product_id: h
        for h in db.query(ProductHistory)
        .filter_by(client_id=client_id, is_current=True)
        .all()
    }

    batch_counter = 0

    # ----------------------------
    # Process rows
    # ----------------------------
    for excel_row in rows:

        row_data = {}
        for idx, col_name in enumerate(headers):
            row_data[col_name] = normalize(excel_row[idx], col_name)

        manufacturer = row_data.get("manufacturer")
        mpn = row_data.get("manufacturer_part_number")

        if not manufacturer or not mpn:
            skipped += 1
            continue

        identity_sig = identity_signature(row_data)
        history_sig = history_signature(row_data)

        product = existing_products.get((manufacturer, mpn))

        # ----------------------------------
        # NEW PRODUCT
        # ----------------------------------
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

            db.add(ProductDim(product_id=product.product_id, **dim_payload))

            existing_products[(manufacturer, mpn)] = product
            inserted += 1
            batch_counter += 1

        # ----------------------------------
        # EXISTING PRODUCT
        # ----------------------------------
        else:
            current = current_histories.get(product.product_id)

            if current and current.row_signature == history_sig:
                skipped += 1
                continue

            if current:
                current.is_current = False

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
            if dim:
                for f in DIM_FIELDS:
                    value = row_data.get(f)
                    if value is not None:
                        setattr(dim, f, value)

            updated += 1
            batch_counter += 1

        # ----------------------------------
        # Commit in batches
        # ----------------------------------
        if batch_counter >= BATCH_SIZE:
            db.commit()
            batch_counter = 0

    db.commit()

    # Clear cache
    redis_client.delete(f"products:client:{client_id}")

    # Save file to S3
    file.file.seek(0)
    if inserted or updated:
        s3.save_uploaded_file(db, client_id, file, user_email, "gsa_upload")

    return {
        "status_code": 201 if inserted or updated else 200,
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }
