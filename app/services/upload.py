from datetime import datetime
from openpyxl import load_workbook
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

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


BATCH_SIZE = 500


def upload_products(db: Session, client_id: int, file, user_email: str):

    # ----------------------------
    # Validate client
    # ----------------------------
    if not db.query(ClientProfile.client_id).filter_by(client_id=client_id).first():
        raise HTTPException(status_code=404, detail="Client Not Found")

    if not db.query(ClientContracts.client_id).filter_by(client_id=client_id).first():
        raise HTTPException(status_code=404, detail="No Contract Found")

    # ----------------------------
    # Load Excel STREAM MODE
    # ----------------------------
    file.file.seek(0)
    wb = load_workbook(file.file, read_only=True, data_only=True)
    sheet = wb.active

    rows = sheet.iter_rows(values_only=True)

    next(rows)  # skip row 1
    headers = [h for h in next(rows)]

    inserted = 0
    updated = 0
    skipped = 0
    batch_counter = 0

    # ----------------------------
    # Preload ONLY KEYS (lightweight)
    # ----------------------------
    existing_keys = set(
        db.execute(
            select(
                ProductMaster.manufacturer,
                ProductMaster.manufacturer_part_number,
                ProductMaster.product_id,
                ProductMaster.row_signature
            ).where(ProductMaster.client_id == client_id)
        ).all()
    )

    # Map for quick lookup
    product_lookup = {
        (m, mpn): (pid, sig)
        for (m, mpn, pid, sig) in existing_keys
    }

    # Preload current history signatures
    history_lookup = dict(
        db.execute(
            select(
                ProductHistory.product_id,
                ProductHistory.row_signature
            ).where(
                ProductHistory.client_id == client_id,
                ProductHistory.is_current == True
            )
        ).all()
    )

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

        existing = product_lookup.get((manufacturer, mpn))

        # ----------------------------------
        # NEW PRODUCT
        # ----------------------------------
        if not existing:

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

            product_lookup[(manufacturer, mpn)] = (
                product.product_id,
                identity_sig,
            )

            history_lookup[product.product_id] = history_sig

            inserted += 1
            batch_counter += 1

        # ----------------------------------
        # EXISTING PRODUCT
        # ----------------------------------
        else:

            product_id, old_identity_sig = existing
            current_history_sig = history_lookup.get(product_id)

            if current_history_sig == history_sig:
                skipped += 1
                continue

            # Mark old history not current
            db.query(ProductHistory).filter_by(
                product_id=product_id,
                is_current=True
            ).update({"is_current": False})

            history_payload = {
                f: row_data.get(f)
                for f in HISTORY_FIELDS
                if row_data.get(f) is not None
            }
            history_payload["currency"] = history_payload.get("currency") or "USD"

            db.add(
                ProductHistory(
                    product_id=product_id,
                    client_id=client_id,
                    row_signature=history_sig,
                    is_current=True,
                    **history_payload,
                )
            )

            # Update master
            db.query(ProductMaster).filter_by(
                product_id=product_id
            ).update(
                {
                    **{
                        f: row_data.get(f)
                        for f in MASTER_FIELDS
                        if row_data.get(f) is not None
                    },
                    "row_signature": identity_sig
                }
            )

            # Update dimension
            db.query(ProductDim).filter_by(
                product_id=product_id
            ).update(
                {
                    f: row_data.get(f)
                    for f in DIM_FIELDS
                    if row_data.get(f) is not None
                }
            )

            history_lookup[product_id] = history_sig
            updated += 1
            batch_counter += 1

        # ----------------------------------
        # Batch Commit + Memory Cleanup
        # ----------------------------------
        if batch_counter >= BATCH_SIZE:
            db.commit()
            db.expunge_all()
            batch_counter = 0

    db.commit()
    db.expunge_all()

    # ----------------------------
    # Clear Cache
    # ----------------------------
    redis_client.delete(f"products:client:{client_id}")

    # ----------------------------
    # Save file to S3 (only if changed)
    # ----------------------------
    if inserted or updated:
        file.file.seek(0)
        s3.save_uploaded_file(
            db, client_id, file, user_email, "gsa_upload"
        )

    return {
        "status_code": 201 if inserted or updated else 200,
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }
