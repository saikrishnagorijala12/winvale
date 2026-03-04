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
from app.utils import s3_upload as s3

HEADER_ALIASES = {

    "manufacturer": [
        "manufacturer",
        "manufacturer_name",
        "mfr",
        "mfr_name",
        "brand",
        "brand_name",
        "maker",
        "supplier",
    ],

    "part_number": [
        "part_number",
        "part_no",
        "manufacturer_part_number",
        "mpn",
        "pn",
        "sku",
        "item_number",
        "item_no",
        "model_number",
        "model_no",
        "product_code",
    ],

    "product_name": [
        "product_name",
        "item_name",
        "name",
        "product",
        "product_title",
        "item_title",
        "model_name",
        "model",
    ],

    "product_description": [
        "product_description",
        "description",
        "item_description",
        "short_description",
        "long_description",
        "desc",
        "item_desc",
        "product_desc",
        "details",
        "specs",
        "specifications",
    ],

    "commercial_list_price_(gv)": [
        "commercial_list_price_(gv)",
        "commercial_list_price",
        "commercial_price",
        "list_price",
        "price",
        "unit_price",
        "msrp",
        "suggested_msrp",
        "market_price",
        "market_rate",
        "selling_price",
        "catalog_price",
        "dealer_price",
        "customer_price",
    ],

    "country_of_origin_(coo)": [
        "country_of_origin_(coo)",
        "country_of_origin",
        "coo",
        "origin_country",
        "origin",
        "made_in",
        "manufactured_in",
        "country_origin",
    ],
}

def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:

    normalized_cols = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]", "_", regex=True)
        .str.replace("_+", "_", regex=True)
    )

    rename_map = {}

    for col in normalized_cols:
        for canonical, aliases in HEADER_ALIASES.items():
            if col in aliases:
                rename_map[col] = canonical
                break

    df.columns = normalized_cols
    df = df.rename(columns=rename_map)

    return df

def build_alias_set():
    aliases = set()

    for vals in HEADER_ALIASES.values():
        for v in vals:
            normalized = (
                v.strip()
                .lower()
                .replace("-", "_")
            )
            normalized = (
                pd.Series([normalized])
                .str.replace(r"[^\w]", "_", regex=True)
                .str.replace("_+", "_", regex=True)
                .iloc[0]
            )

            aliases.add(normalized)

    return aliases


def normalize_str(v):
    if v is None or pd.isna(v):
        return None
    return str(v).strip()


def normalize_upper(v):
    if v is None or pd.isna(v):
        return None
    return str(v).strip().upper()


def product_identity(manufacturer, mpn):
    m = normalize_upper(manufacturer)
    p = normalize_upper(mpn)
    if not m or not p:
        return None
    return (m, p)


def parse_price(value):
    if value is None or pd.isna(value):
        return None

    s = str(value).strip()
    if not s:
        return None

    s = s.replace("$", "").replace(",", "")

    try:
        d = Decimal(s)
    except (InvalidOperation, ValueError):
        return None

    if not d.is_finite():
        return None

    return d.quantize(Decimal("0.01"))


def clean(value):
    if pd.isna(value):
        return None
    return str(value).strip()


def safe_compare(a, b):
    return (a or "").strip() != (b or "").strip()

ALIAS_SET = build_alias_set()

def find_header_row(df: pd.DataFrame) -> int:

    for i in range(min(30, len(df))):

        row = (
            df.iloc[i]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r"[^\w]", "_", regex=True)
            .str.replace("_+", "_", regex=True)
        )

        matches = set(row.values) & ALIAS_SET

        if len(matches) >= 3:
            return i

    raise HTTPException(
        status_code=400,
        detail="Could not detect header row in CPL file",
    )


def upload_cpl_service(
    db: Session,
    client_id: int,
    file,
    user_email: str,
):

    job = create_job(db, client_id, user_email)
    job_id = job["job_id"]

    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    raw_df = pd.read_excel(BytesIO(file.file.read()), header=None)

    required_cols = {
    "manufacturer",
    "part_number",
    "product_description",
    "commercial_list_price_(gv)",
    }

    header_row = find_header_row(raw_df)

    df = raw_df.iloc[header_row + 1:].copy()
    df.columns = raw_df.iloc[header_row]
    df.reset_index(drop=True, inplace=True)

    df = normalize_headers(df)

    missing = required_cols - set(df.columns)

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing)}"
        )

    cpl_map = {}

    products = (
            db.query(ProductMaster)
            .filter_by(client_id=client_id, is_deleted=False)
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

    for _, row in df.iterrows():

        key = product_identity(
            row["manufacturer"],
            row["part_number"],
        )

        if not key:
            continue
                
        product = product_map.get(key)
        price = parse_price(row.get("commercial_list_price_(gv)"))
        desc = clean(row.get("product_description"))
        coo = normalize_upper(row.get("country_of_origin_(coo)"))

        name = (
            clean(row.get("product_name"))
            or (product.item_name if product else None)
            or "N/A"
        )

        cpl = CPLList(
            client_id=client_id,
            manufacturer_name=normalize_upper(row["manufacturer"]),
            manufacturer_part_number=str(row["part_number"]).strip(),
            item_name=name,
            item_description=desc,
            commercial_list_price=price,
            origin_country=coo,
            uploaded_by=user.user_id,
        )

        db.add(cpl)

        cpl_map[key] = {
            "cpl": cpl,
            "price": price,
            "description": desc,
            "name": name,
        }

    db.flush()

    summary = {
        "new_products": 0,
        "removed_products": 0,
        "price_increase": 0,
        "price_decrease": 0,
        "description_changed": 0,
        "name_changed": 0,
        "no_change": 0,
    }

    processed_keys = set()

    for key, cpl_data in cpl_map.items():

        cpl = cpl_data["cpl"]
        product = product_map.get(key)

        if not product:

            summary["new_products"] += 1

            db.add(
                ModificationAction(
                    user_id=user.user_id,
                    client_id=client_id,
                    job_id=job_id,
                    cpl_id=cpl.cpl_id,
                    product_id=None,
                    action_type="NEW_PRODUCT",
                    old_price=None,
                    new_price=cpl_data["price"],
                    old_description=None,
                    new_description=cpl_data["description"],
                    old_name=None,
                    new_name=cpl_data["name"],
                    number_of_items_impacted=1,
                )
            )

            continue

        processed_keys.add(key)

        old_price = product.commercial_price
        new_price = cpl_data["price"]

        old_desc = product.item_description
        new_desc = cpl_data["description"]

        old_name = product.item_name
        new_name = cpl_data["name"]

        price_changed = old_price != new_price
        desc_changed = safe_compare(old_desc, new_desc)
        name_changed = safe_compare(old_name, new_name)

        actions_created = False

        if price_changed:
            if old_price is None or (new_price is not None and new_price > old_price):
                action_type = "PRICE_INCREASE"
                summary["price_increase"] += 1
            else:
                action_type = "PRICE_DECREASE"
                summary["price_decrease"] += 1

            db.add(
                ModificationAction(
                    user_id=user.user_id,
                    client_id=client_id,
                    job_id=job_id,
                    cpl_id=cpl.cpl_id,
                    product_id=product.product_id,
                    action_type=action_type,
                    old_price=old_price,
                    new_price=new_price,
                    number_of_items_impacted=1,
                )
            )
            actions_created = True


        if desc_changed:
            summary["description_changed"] += 1

            db.add(
                ModificationAction(
                    user_id=user.user_id,
                    client_id=client_id,
                    job_id=job_id,
                    cpl_id=cpl.cpl_id,
                    product_id=product.product_id,
                    action_type="DESCRIPTION_CHANGE",
                    old_description=old_desc,
                    new_description=new_desc,
                    number_of_items_impacted=1,
                )
            )
            actions_created = True


        if name_changed:
            summary["name_changed"] += 1

            db.add(
                ModificationAction(
                    user_id=user.user_id,
                    client_id=client_id,
                    job_id=job_id,
                    cpl_id=cpl.cpl_id,
                    product_id=product.product_id,
                    action_type="NAME_CHANGE",
                    old_name=old_name,
                    new_name=new_name,
                    number_of_items_impacted=1,
                )
            )
            actions_created = True


        if not actions_created:
            summary["no_change"] += 1

    for key, product in product_map.items():

        if key not in processed_keys:

            summary["removed_products"] += 1

            db.add(
                ModificationAction(
                    user_id=user.user_id,
                    client_id=client_id,
                    job_id=job_id,
                    cpl_id=None,
                    product_id=product.product_id,
                    action_type="REMOVED_PRODUCT",
                    old_price=product.commercial_price,
                    new_price=None,
                    old_description=product.item_description,
                    new_description=None,
                    old_name=product.item_name,
                    new_name=None,
                    number_of_items_impacted=1,
                )
            )

    db.commit()

    s3.save_uploaded_file(db, client_id, file, user_email, "cpl_upload")

    return {
        "job_id": job_id,
        "client_id": client_id,
        "status": "pending",
        "summary": summary,
        "next_step": "Approve or reject job",
    }
