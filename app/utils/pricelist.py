from decimal import Decimal, InvalidOperation
import pandas as pd
from fastapi import HTTPException

HEADER_ALIASES = {
    "manufacturer": [
        "manufacturer",
        "manufacturer_name",
        "mfr",
        "mfr_name",
    ],

    "part_number": [
        "part_number",
        "part_no",
        "manufacturer_part_number",
        "mpn",
        "pn",
    ],

    "product_name": [
        "product_name",
        "item_name",
        "name",
        "product_name",
    ],

    "product_description": [
        "product_description",
        "description",
        "item_description",
        "short_description",
        "long_description",
        "product_description",
    ],

    "commercial_list_price_(gv)": [
        "commercial_list_price_(gv)",
        "commercial_list_price_gv",
        "commercial_list_price",
        "commercial_price_list",
        "cpl",
        "commercial_price",
        "list_price",
        "price",
        "msrp",
        "suggested_msrp",
        "market_price",
        "market_rate",
    ],

    "country_of_origin_(coo)": [
        "country_of_origin_(coo)",
        "country_of_origin",
        "coo",
        "origin_country",
    ],
}

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

ALIAS_SET = build_alias_set()

def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:

    normalized_cols = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]", "_", regex=True)
        .str.replace("_+", "_", regex=True)
        .str.strip("_")
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
    if not p:
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
