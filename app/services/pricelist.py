from io import BytesIO
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    User,
    Job,
    CPLList,
    ProductMaster,
    ModificationAction,
)
from app.services.jobs import create_job
from app.utils.name_to_id import get_status_id_by_name


def upload_cpl(
    db: Session,
    client_id: int,
    file,
    user_email: str,
):
    job_response = create_job(db, client_id, user_email)
    job_id = job_response["job_id"]

    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(401, "Invalid user")

    df = pd.read_excel(BytesIO(file.file.read()))
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    required_cols = {
        "manufacturer",
        "manufacturer_part_number",
        "item_name",
        "commercial_price",
        "item_description",
    }

    if not required_cols.issubset(df.columns):
        raise HTTPException(400, "Invalid CPL format")

    db.query(CPLList).filter_by(client_id=client_id).delete()

    cpl_map = {}

    for _, row in df.iterrows():
        key = (row["manufacturer"], row["manufacturer_part_number"])

        cpl = CPLList(
            client_id=client_id,
            manufacturer_name=row["manufacturer"],
            manufacturer_part_number=row["manufacturer_part_number"],
            item_name=row["item_name"],
            item_description=row.get("item_description"),
            commercial_list_price=row.get("commercial_price"),
            uploaded_by=user.user_id,
        )
        db.add(cpl)

        cpl_map[key] = row

    db.flush()

    products = (
        db.query(ProductMaster)
        .filter_by(client_id=client_id)
        .all()
    )

    product_map = {
        (p.manufacturer, p.manufacturer_part_number): p
        for p in products
    }

    summary = {
        "new_products": 0,
        "removed_products": 0,
        "price_increase": 0,
        "price_decrease": 0,
        "description_changed": 0,
    }

    for key, cpl_row in cpl_map.items():
        product = product_map.get(key)

        if not product:
            summary["new_products"] += 1
            _add_action(db, user, client_id, job_id, "NEW_PRODUCT")
            continue

        old_price = product.commercial_list_price
        new_price = cpl_row.get("commercial_price")

        if old_price != new_price:
            if new_price > old_price:
                summary["price_increase"] += 1
                action = "PRICE_INCREASE"
            else:
                summary["price_decrease"] += 1
                action = "PRICE_DECREASE"

            db.add(
                ModificationAction(
                    user_id=user.user_id,
                    client_id=client_id,
                    job_id=job_id,
                    action_type=action,
                    old_price=old_price,
                    new_price=new_price,
                    number_of_items_impacted=1,
                )
            )

        if product.item_description != cpl_row.get("item_description"):
            summary["description_changed"] += 1
            db.add(
                ModificationAction(
                    user_id=user.user_id,
                    client_id=client_id,
                    job_id=job_id,
                    action_type="DESCRIPTION_CHANGE",
                    old_description=product.item_description,
                    new_description=cpl_row.get("item_description"),
                    number_of_items_impacted=1,
                )
            )

    for key in product_map:
        if key not in cpl_map:
            summary["removed_products"] += 1
            _add_action(db, user, client_id, job_id, "REMOVED_PRODUCT")

    db.commit()

    return {
        "job_id": job_id,
        "client_id": client_id,
        "status": "pending",
        "summary": summary,
        "next_step": "Approve or reject job",
    }


def _add_action(db, user, client_id, job_id, action_type):
    db.add(
        ModificationAction(
            user_id=user.user_id,
            client_id=client_id,
            job_id=job_id,
            action_type=action_type,
            number_of_items_impacted=1,
        )
    )