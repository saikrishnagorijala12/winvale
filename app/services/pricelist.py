from io import BytesIO
from decimal import Decimal, InvalidOperation
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    User,
    ProductMaster,
    CPLList,
    ModificationAction,
)
from app.services.jobs import create_job


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def normalize_str(v):
    if v is None:
        return None
    return str(v).strip().upper()


def product_identity(manufacturer, mpn):
    m = normalize_str(manufacturer)
    p = normalize_str(mpn)
    if not m or not p:
        return None
    return (m, p)


def parse_price(value):
    """
    Normalizes CPL prices.
    Handles:
    - $100.00
    - 100
    - 100.00
    - NaN / empty / garbage
    Returns Decimal or None
    """
    if value is None:
        return None

    # Pandas NaN
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    s = str(value).strip()
    if not s:
        return None

    # Remove currency symbols and commas
    s = s.replace("$", "").replace(",", "")

    try:
        d = Decimal(s)
    except (InvalidOperation, ValueError):
        return None

    # Kill NaN / Infinity
    if not d.is_finite():
        return None

    return d.quantize(Decimal("0.01"))


# -------------------------------------------------
# CPL Upload Service
# -------------------------------------------------

def upload_cpl_service(
    db: Session,
    client_id: int,
    file,
    user_email: str,
):

    # Create job
    job = create_job(db, client_id, user_email)
    job_id = job["job_id"]

    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    # -------------------------------------------------
    # Read CPL Excel
    # -------------------------------------------------
    df = pd.read_excel(BytesIO(file.file.read()), header=None)

    # CPL format (fragile by definition)
    df.columns = df.iloc[4]
    df = df.iloc[6:].reset_index(drop=True)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    required_cols = {
        "manufacturer",
        "part_number",
        "product_name",
        "product_description",
        "commercial_list_price_(gv)",
    }

    if not required_cols.issubset(df.columns):
        raise HTTPException(status_code=400, detail="Invalid CPL file format")

    # -------------------------------------------------
    # Clear existing CPL
    # -------------------------------------------------
    db.query(CPLList).filter_by(client_id=client_id).delete()

    # -------------------------------------------------
    # Load CPL rows
    # -------------------------------------------------
    cpl_map = {}

    for _, row in df.iterrows():
        key = product_identity(
            row["manufacturer"],
            row["part_number"],
        )
        if not key:
            continue

        price = parse_price(row["commercial_list_price_(gv)"])
        desc = row.get("product_description")

        cpl_map[key] = {
            "price": price,
            "description": desc,
        }

        db.add(
            CPLList(
                client_id=client_id,
                manufacturer_name=row["manufacturer"],
                manufacturer_part_number=row["part_number"],
                item_name=row["product_name"],
                item_description=desc,
                commercial_list_price=price,
                uploaded_by=user.user_id,
            )
        )

    db.flush()

    # -------------------------------------------------
    # Load products
    # -------------------------------------------------
    products = (
        db.query(ProductMaster)
        .filter_by(client_id=client_id)
        .all()
    )

    product_map = {}
    for p in products:
        key = product_identity(
            p.manufacturer,
            p.manufacturer_part_number,
        )
        if key:
            product_map[key] = p

    # -------------------------------------------------
    # Compare CPL vs ProductMaster
    # -------------------------------------------------
    summary = {
        "new_products": 0,
        "removed_products": 0,
        "price_increase": 0,
        "price_decrease": 0,
        "description_changed": 0,
        "no_change": 0,
    }

    processed_keys = set()

    for key, cpl in cpl_map.items():
        product = product_map.get(key)

        # -------------------------
        # NEW PRODUCT
        # -------------------------
        if not product:
            summary["new_products"] += 1
            db.add(
                ModificationAction(
                    user_id=user.user_id,
                    client_id=client_id,
                    job_id=job_id,
                    product_id=None,
                    action_type="NEW_PRODUCT",
                    old_price=None,
                    new_price=cpl["price"],
                    old_description=None,
                    new_description=cpl["description"],
                    number_of_items_impacted=1,
                )
            )
            continue

        processed_keys.add(key)

        old_price = product.commercial_price
        new_price = cpl["price"]

        old_desc = product.item_description
        new_desc = cpl["description"]

        price_changed = old_price != new_price
        desc_changed = old_desc != new_desc

        # -------------------------
        # PRICE CHANGE (SAFE)
        # -------------------------
        if price_changed:
            if old_price is None and new_price is not None:
                action = "PRICE_INCREASE"
                summary["price_increase"] += 1

            elif old_price is not None and new_price is None:
                action = "PRICE_DECREASE"
                summary["price_decrease"] += 1

            else:  # both not None
                if new_price > old_price:
                    action = "PRICE_INCREASE"
                    summary["price_increase"] += 1
                else:
                    action = "PRICE_DECREASE"
                    summary["price_decrease"] += 1

        elif desc_changed:
            action = "DESCRIPTION_CHANGE"
            summary["description_changed"] += 1

        else:
            action = "NO_CHANGE"
            summary["no_change"] += 1

        db.add(
            ModificationAction(
                user_id=user.user_id,
                client_id=client_id,
                job_id=job_id,
                product_id=product.product_id,
                action_type=action,
                old_price=old_price,
                new_price=new_price,
                old_description=old_desc,
                new_description=new_desc,
                number_of_items_impacted=1,
            )
        )

    # -------------------------------------------------
    # REMOVED PRODUCTS
    # -------------------------------------------------
    for key, product in product_map.items():
        if key not in processed_keys:
            summary["removed_products"] += 1
            db.add(
                ModificationAction(
                    user_id=user.user_id,
                    client_id=client_id,
                    job_id=job_id,
                    product_id=product.product_id,
                    action_type="REMOVED_PRODUCT",
                    old_price=product.commercial_price,
                    new_price=None,
                    old_description=product.item_description,
                    new_description=None,
                    number_of_items_impacted=1,
                )
            )

    db.commit()

    return {
        "job_id": job_id,
        "client_id": client_id,
        "status": "pending",
        "summary": summary,
        "next_step": "Approve or reject job",
    }
