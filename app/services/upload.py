from io import BytesIO
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from math import isnan

from app.models.client_profiles import ClientProfile
from app.models.product_master import ProductMaster
from app.models.product_history import ProductHistory
from app.models.product_dim import ProductDim
from app.utils.upload_helper import MASTER_FIELDS, DIM_FIELDS, HISTORY_FIELDS, history_changed


def clean(value):
    if value is None:
        return None

    if isinstance(value, float) and isnan(value):
        return None

    if isinstance(value, (int, float)):
        return str(int(value)) if value == int(value) else str(value)

    return str(value).strip()


def upload_products(db: Session, client_id: int, file):
    client = (
        db.query(ClientProfile)
        .filter(ClientProfile.client_id == client_id)
        .first()
    )
    if not client:
        return None

    contents = file.file.read()

    raw_df = pd.read_excel(BytesIO(contents), header=None)
    raw_df = raw_df.drop(index=0).reset_index(drop=True)
    raw_df.columns = raw_df.iloc[0]
    df = raw_df.drop(index=0).reset_index(drop=True)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

    inserted = 0
    updated = 0

    for _, row in df.iterrows():
        mfg_part = clean(row.get("manufacturer_part_number"))
        if not mfg_part:
            continue

        product = (
            db.query(ProductMaster)
            .filter(
                ProductMaster.client_id == client_id,
                ProductMaster.manufacturer_part_number == mfg_part,
            )
            .first()
        )

        if not product:
            product_data = {f: clean(row.get(f)) for f in MASTER_FIELDS}

            product = ProductMaster(
                client_id=client_id,
                **product_data,
            )
            db.add(product)
            db.flush()

            history_data = {f: clean(row.get(f)) for f in HISTORY_FIELDS}
            db.add(
                ProductHistory(
                    product_id=product.product_id,
                    client_id=client_id,
                    is_current=True,
                    **history_data,
                )
            )

            dim_data = {f: clean(row.get(f)) for f in DIM_FIELDS}
            db.add(
                ProductDim(
                    product_id=product.product_id,
                    **dim_data,
                )
            )

            inserted += 1
            continue

        current = (
            db.query(ProductHistory)
            .filter(
                ProductHistory.product_id == product.product_id,
                ProductHistory.is_current.is_(True),
            )
            .first()
        )

        if current and not history_changed(current, row):
            continue

        if current:
            current.is_current = False
            current.effective_end_date = datetime.utcnow()

        history_data = {f: clean(row.get(f)) for f in HISTORY_FIELDS}
        db.add(
            ProductHistory(
                product_id=product.product_id,
                client_id=client_id,
                is_current=True,
                **history_data,
            )
        )

        for field in MASTER_FIELDS:
            setattr(product, field, clean(row.get(field)))

        updated += 1

    db.commit()

    return {
        "inserted": inserted,
        "updated": updated,
    }
