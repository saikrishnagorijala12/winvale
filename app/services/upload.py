from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from app.models.client_profiles import ClientProfile
from app.models.product_master import ProductMaster
from app.models.product_history import ProductHistory
from app.models.product_dim import ProductDim
from app.schemas.upload import ProductUploadRow


def upload_products(
    db: Session,
    client_id: int,
    payload: List[ProductUploadRow]
):
    client = (
        db.query(ClientProfile)
        .filter(ClientProfile.client_id == client_id)
        .first()
    )

    if not client:
        return None

    now = datetime.now(timezone.utc)

    master = (
        db.query(ProductMaster)
        .filter(ProductMaster.client_id == client_id)
        .first()
    )

    created = 0
    updated = 0

    for row in payload:
        if not master:
            master = ProductMaster(
                client_id=client_id,
                item_type=row.item_type,
                item_name=row.item_name,
                item_description=row.item_description,
                manufacturer=row.manufacturer,
                manufacturer_part_number=row.manufacturer_part_number,
                client_part_number=row.client_part_number,
                sin=row.sin,
                commercial_list_price=row.commercial_list_price,
                country_of_origin=row.country_of_origin,
                recycled_content_percent=row.recycled_content_percent,
                uom=row.uom,
                quantity_per_pack=row.quantity_per_pack,
                quantity_unit_uom=row.quantity_unit_uom,
                nsn=row.nsn,
                upc=row.upc,
                unspsc=row.unspsc,
                hazmat=row.hazmat,
                product_info_code=row.product_info_code,
                url_508=row.url_508,
                product_url=row.product_url
            )
            db.add(master)
            db.flush()

            created += 1
        else:
            updated += 1

        current_hist = (
            db.query(ProductHistory)
            .filter(
                ProductHistory.client_id == client_id,
                ProductHistory.is_current == True
            )
            .first()
        )

        if current_hist:
            current_hist.is_current = False
            current_hist.effective_end_date = now

        db.add(ProductHistory(
            product_id=master.product_id,
            client_id=client_id,
            item_type=row.item_type,
            item_name=row.item_name,
            item_description=row.item_description,
            manufacturer=row.manufacturer,
            manufacturer_part_number=row.manufacturer_part_number,
            client_part_number=row.client_part_number,
            sin=row.sin,
            country_of_origin=row.country_of_origin,
            recycled_content_percent=row.recycled_content_percent,
            uom=row.uom,
            quantity_per_pack=row.quantity_per_pack,
            quantity_unit_uom=row.quantity_unit_uom,
            nsn=row.nsn,
            upc=row.upc,
            unspsc=row.unspsc,
            hazmat=row.hazmat,
            product_info_code=row.product_info_code,
            url_508=row.url_508,
            product_url=row.product_url,
            is_current=True,
            effective_start_date=now
        ))

        master.item_type = row.item_type
        master.item_name = row.item_name
        master.item_description = row.item_description
        master.manufacturer = row.manufacturer
        master.manufacturer_part_number = row.manufacturer_part_number
        master.client_part_number = row.client_part_number
        master.sin = row.sin
        master.commercial_list_price = row.commercial_list_price
        master.country_of_origin = row.country_of_origin
        master.recycled_content_percent = row.recycled_content_percent
        master.uom = row.uom
        master.quantity_per_pack = row.quantity_per_pack
        master.quantity_unit_uom = row.quantity_unit_uom
        master.nsn = row.nsn
        master.upc = row.upc
        master.unspsc = row.unspsc
        master.hazmat = row.hazmat
        master.product_info_code = row.product_info_code
        master.url_508 = row.url_508
        master.product_url = row.product_url

        dim = (
            db.query(ProductDim)
            .filter(ProductDim.product_id == master.product_id)
            .first()
        )

        if not dim:
            dim = ProductDim(product_id=master.product_id)
            db.add(dim)

        dim.length = row.length
        dim.width = row.width
        dim.height = row.height
        dim.physical_uom = row.physical_uom
        dim.weight_lbs = row.weight_lbs
        dim.warranty_period = row.warranty_period

    db.commit()

    return {
        "created": created,
        "updated": updated
    }
