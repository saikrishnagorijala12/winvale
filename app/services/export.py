from sqlalchemy.orm import Session, joinedload
from openpyxl import Workbook
from app.utils.gsa_header import GSA_HEADERS
from app.models.product_master import ProductMaster


def export_products_excel(db: Session, client_id: int):
    products = (
        db.query(ProductMaster)
        .filter(ProductMaster.client_id == client_id)
        .options(joinedload(ProductMaster.dimension))
        .all()
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Products"

    ws.append(GSA_HEADERS)

    for p in products:
        d = p.dimension

        ws.append([
            p.item_type,
            p.manufacturer,
            p.manufacturer_part_number,
            p.client_part_number,
            p.sin,
            p.item_name,
            p.item_description,
            float(p.recycled_content_percent) if p.recycled_content_percent is not None else None,
            p.uom,
            p.quantity_per_pack,
            p.quantity_unit_uom,
            float(p.commercial_list_price) if p.commercial_list_price is not None else None,
            None,
            None,
            None,
            None,
            p.country_of_origin,
            None,
            None,
            None,
            None,
            None,
            None,
            p.nsn,
            p.upc,
            p.unspsc,
            None,
            None,
            None,
            d.photo_path if d and d.photo_path else None,
            None,
            None,
            None,
            p.product_url,
            d.warranty_period if d and d.warranty_period is not None else None,
            None,
            float(d.length) if d and d.length is not None else None,
            float(d.width) if d and d.width is not None else None,
            float(d.height) if d and d.height is not None else None,
            d.physical_uom if d and d.physical_uom else None,
            float(d.weight_lbs) if d and d.weight_lbs is not None else None,
            p.product_info_code,
            p.url_508,
            p.hazmat,
            None,
            None,
            None,
        ])


    return wb
