from sqlalchemy.orm import Session, joinedload
from openpyxl import Workbook
from app.models.product_master import ProductMaster
from app.models.client_profiles import ClientProfile
from datetime import datetime, timezone
from typing import Optional


def export_products_excel(db: Session, client_id: Optional[int] = None):
    query = (
        db.query(ProductMaster)
        .options(
            joinedload(ProductMaster.dimension),
            joinedload(ProductMaster.client)
        )
    )

    if client_id is not None:
        query = query.filter(ProductMaster.client_id == client_id)

    products = query.all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Products"

    headers = [
        "item_type",
        "manufacturer",
        "manufacturer_part_number",
        "vendor_part_number",
        "sin",
        "item_name",
        "item_description",
        "recycled_content_percent",
        "uom",
        "quantity_per_pack",
        "quantity_unit_uom",
        "commercial_price",
        "mfc_name",
        "mfc_price",
        "govt_price_no_fee",
        "govt_price_with_fee",
        "country_of_origin",
        "delivery_days",
        "lead_time_code",
        "fob_us",
        "fob_ak",
        "fob_hi",
        "fob_pr",
        "nsn",
        "upc",
        "unspsc",
        "sale_price_with_fee",
        "start_date",
        "stop_date",
        "default_photo",
        "photo_2",
        "photo_3",
        "photo_4",
        "product_url",
        "warranty_period",
        "warranty_unit_of_time",
        "length",
        "width",
        "height",
        "physical_uom",
        "weight_lbs",
        "product_info_code",
        "url_508",
        "hazmat",
        "dealer_cost",
        "mfc_markup_percentage",
        "govt_markup_percentage",
    ]

    if client_id is None:
        headers.insert(0, "client_name")

    ws.append(headers)

    for p in products:
        d = p.dimension

        row = [
            p.item_type,
            p.manufacturer,
            p.manufacturer_part_number,
            p.vendor_part_number,
            p.sin,
            p.item_name,
            p.item_description,
            float(p.recycled_content_percent) if p.recycled_content_percent is not None else None,
            p.uom,
            p.quantity_per_pack,
            p.quantity_unit_uom,
            float(p.commercial_price) if p.commercial_price is not None else None,
            p.mfc_name,
            float(p.mfc_price) if p.mfc_price is not None else None,
            float(p.govt_price_no_fee) if p.govt_price_no_fee is not None else None,
            float(p.govt_price_with_fee) if p.govt_price_with_fee is not None else None,
            p.country_of_origin,
            p.delivery_days,
            p.lead_time_code,
            p.fob_us,
            p.fob_ak,
            p.fob_hi,
            p.fob_pr,
            p.nsn,
            p.upc,
            p.unspsc,
            float(p.sale_price_with_fee) if p.sale_price_with_fee is not None else None,
            p.start_date,
            p.stop_date,
            p.default_photo,
            p.photo_2,
            p.photo_3,
            p.photo_4,
            p.product_url,
            p.warranty_period,
            p.warranty_unit_of_time,
            float(d.length) if d and d.length is not None else None,
            float(d.width) if d and d.width is not None else None,
            float(d.height) if d and d.height is not None else None,
            d.physical_uom if d else None,
            float(d.weight_lbs) if d and d.weight_lbs is not None else None,
            p.product_info_code,
            p.url_508,
            p.hazmat,
            float(p.dealer_cost) if p.dealer_cost is not None else None,
            float(p.mfc_markup_percentage) if p.mfc_markup_percentage is not None else None,
            float(p.govt_markup_percentage) if p.govt_markup_percentage is not None else None,
        ]

        if client_id is None:
            row.insert(0, p.client.company_name if p.client else None)

        ws.append(row)

    return wb


def get_master_filename(db: Session, client_id: Optional[int] = None):
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if client_id is not None:
        client = db.query(ClientProfile).filter_by(client_id=client_id).first()
        if client:
            return f"{client.company_name}_products_{date_str}.xlsx"

    return f"all_products_{date_str}.xlsx"
