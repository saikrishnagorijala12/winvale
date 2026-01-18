from io import BytesIO
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

from app.models.client_profiles import ClientProfile
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


def upload_products(db: Session, client_id: int, file):
    if not db.query(ClientProfile).filter_by(client_id=client_id).first():
        raise ValueError("Invalid client")

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
            product = ProductMaster(
                client_id=client_id,
                row_signature=identity_sig,
                **{f: row_data.get(f) for f in MASTER_FIELDS},
            )
            db.add(product)
            db.flush()

            db.add(
                ProductHistory(
                    product_id=product.product_id,
                    client_id=client_id,
                    row_signature=history_sig,
                    is_current=True,
                    **{f: row_data.get(f) for f in HISTORY_FIELDS},
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

        db.add(
            ProductHistory(
                product_id=product.product_id,
                client_id=client_id,
                row_signature=history_sig,
                is_current=True,
                **{f: row_data.get(f) for f in HISTORY_FIELDS},
            )
        )

        for f in MASTER_FIELDS:
            setattr(product, f, row_data.get(f))

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

    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
    }
