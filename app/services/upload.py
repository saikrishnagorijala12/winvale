import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.product_master import ProductMaster
from app.models.product_history import ProductHistory
from app.models.product_dim import ProductDim
from app.utils.upload_helper import MASTER_FIELDS, DIM_FIELDS, HISTORY_FIELDS, history_changed
def upload_products(db: Session, client_id: int, file, user_id: int):
    df = pd.read_excel(file.file)

    inserted = 0
    updated = 0

    for _, row in df.iterrows():
        mfg_part = row["manufacturer_part_number"]

        product = (
            db.query(ProductMaster)
            .filter(
                ProductMaster.client_id == client_id,
                ProductMaster.manufacturer_part_number == mfg_part,
            )
            .first()
        )


        if not product:
            product_data = {field: row.get(field) for field in MASTER_FIELDS}
            product = ProductMaster(client_id=client_id, **product_data)

            db.add(product)
            db.flush()

            history_data = {field: row.get(field) for field in HISTORY_FIELDS}
            history = ProductHistory(
                product_id=product.product_id,
                client_id=client_id,
                is_current=True,
                **history_data,
            )
            db.add(history)

            dim_data = {field: row.get(field) for field in DIM_FIELDS}
            dim = ProductDim(product_id=product.product_id, **dim_data)
            db.add(dim)

            inserted += 1
            continue

        current = (
            db.query(ProductHistory)
            .filter(
                ProductHistory.product_id == product.product_id,
                ProductHistory.is_current == True,
            )
            .first()
        )

        if current and not history_changed(current, row):
            continue

        if current:
            current.is_current = False
            current.effective_end_date = datetime.utcnow()

        history_data = {field: row.get(field) for field in HISTORY_FIELDS}
        new_history = ProductHistory(
            product_id=product.product_id,
            client_id=client_id,
            is_current=True,
            **history_data,
        )
        db.add(new_history)

        for field in MASTER_FIELDS:
            setattr(product, field, row.get(field))

        updated += 1

    db.commit()

    return {
        "inserted": inserted,
        "updated": updated,
    }
