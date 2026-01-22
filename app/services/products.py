from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.product_master import ProductMaster
from app.utils.name_to_id import get_status_id_by_name
from sqlalchemy.orm import joinedload


from sqlalchemy.orm import joinedload

def get_all(db: Session):
    products = (
        db.query(ProductMaster)
        .join(ClientProfile, ProductMaster.client)
        .options(
            joinedload(ProductMaster.client),
            joinedload(ProductMaster.dimension),
        )
        .filter(ClientProfile.is_deleted.is_(False))
        .all()
    )

    result = []

    for p in products:
        d = p.dimension

        result.append({
            "product_id": p.product_id,
            "client_id": p.client_id,
            "client_name": p.client.company_name if p.client else None,

            "item_type": p.item_type,
            "item_name": p.item_name,
            "item_description": p.item_description,

            "manufacturer": p.manufacturer,
            "manufacturer_part_number": p.manufacturer_part_number,
            "client_part_number": p.client_part_number,

            "sin": p.sin,
            "commercial_list_price": float(p.commercial_list_price) if p.commercial_list_price is not None else None,

            "country_of_origin": p.country_of_origin,
            "recycled_content_percent": float(p.recycled_content_percent) if p.recycled_content_percent is not None else None,

            "uom": p.uom,
            "quantity_per_pack": p.quantity_per_pack,
            "quantity_unit_uom": p.quantity_unit_uom,

            "nsn": p.nsn,
            "upc": p.upc,
            "unspsc": p.unspsc,

            "hazmat": p.hazmat,
            "product_info_code": p.product_info_code,

            "url_508": p.url_508,
            "product_url": p.product_url,

            "row_signature": p.row_signature,

            "created_time": p.created_time,
            "updated_time": p.updated_time,

            "dim_id": d.dim_id if d else None,

            "length": float(d.length) if d and d.length is not None else None,
            "width": float(d.width) if d and d.width is not None else None,
            "height": float(d.height) if d and d.height is not None else None,

            "physical_uom": d.physical_uom if d else None,

            "weight_lbs": float(d.weight_lbs) if d and d.weight_lbs is not None else None,
            "warranty_period": d.warranty_period if d else None,

            "photo_type": d.photo_type if d else None,
            "photo_path": d.photo_path if d else None,

            "dim_created_time": d.created_time if d else None,
            "dim_updated_time": d.updated_time if d else None,
        })

    return result

from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status

def get_by_id(db: Session, product_id: int):
    product = (
    db.query(ProductMaster)
    .join(ClientProfile, ProductMaster.client)
    .options(
        joinedload(ProductMaster.client),
        joinedload(ProductMaster.dimension),
    )
    .filter(
        ClientProfile.is_deleted.is_(False),
        ProductMaster.product_id == product_id
    )
    .one_or_none()
)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    d = product.dimension 

    return {
        "product_id": product.product_id,
        "client_id": product.client_id,
        "client_name": product.client.company_name if product.client else None,

        "item_type": product.item_type,
        "item_name": product.item_name,
        "item_description": product.item_description,

        "manufacturer": product.manufacturer,
        "manufacturer_part_number": product.manufacturer_part_number,
        "client_part_number": product.client_part_number,

        "sin": product.sin,
        "commercial_list_price": (
            float(product.commercial_list_price)
            if product.commercial_list_price is not None
            else None
        ),

        "country_of_origin": product.country_of_origin,
        "recycled_content_percent": (
            float(product.recycled_content_percent)
            if product.recycled_content_percent is not None
            else None
        ),

        "uom": product.uom,
        "quantity_per_pack": product.quantity_per_pack,
        "quantity_unit_uom": product.quantity_unit_uom,

        "nsn": product.nsn,
        "upc": product.upc,
        "unspsc": product.unspsc,

        "hazmat": product.hazmat,
        "product_info_code": product.product_info_code,

        "url_508": product.url_508,
        "product_url": product.product_url,

        "row_signature": product.row_signature,

        "created_time": product.created_time,
        "updated_time": product.updated_time,

        "dim_id": d.dim_id if d else None,

        "length": float(d.length) if d and d.length is not None else None,
        "width": float(d.width) if d and d.width is not None else None,
        "height": float(d.height) if d and d.height is not None else None,

        "physical_uom": d.physical_uom if d else None,

        "weight_lbs": float(d.weight_lbs) if d and d.weight_lbs is not None else None,
        "warranty_period": d.warranty_period if d else None,

        "photo_type": d.photo_type if d else None,
        "photo_path": d.photo_path if d else None,

        "dim_created_time": d.created_time if d else None,
        "dim_updated_time": d.updated_time if d else None,
    }


def get_by_client(db: Session, client_id: int):

    products = (
    db.query(ProductMaster)
    .join(ClientProfile, ProductMaster.client)
    .options(
        joinedload(ProductMaster.client),
        joinedload(ProductMaster.dimension),
    )
    .filter(
        ClientProfile.is_deleted.is_(False),
        ProductMaster.client_id == client_id
    )
    .all()
)
    

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No products found for given client"
        )

    result = []

    for p in products:
        d = p.dimension  
        result.append({
            "product_id": p.product_id,
            "client_id": p.client_id,
            "client_name": p.client.company_name if p.client else None,

            "item_type": p.item_type,
            "item_name": p.item_name,
            "item_description": p.item_description,

            "manufacturer": p.manufacturer,
            "manufacturer_part_number": p.manufacturer_part_number,
            "client_part_number": p.client_part_number,

            "sin": p.sin,
            "commercial_list_price": (
                float(p.commercial_list_price)
                if p.commercial_list_price is not None
                else None
            ),

            "country_of_origin": p.country_of_origin,
            "recycled_content_percent": (
                float(p.recycled_content_percent)
                if p.recycled_content_percent is not None
                else None
            ),

            "uom": p.uom,
            "quantity_per_pack": p.quantity_per_pack,
            "quantity_unit_uom": p.quantity_unit_uom,

            "nsn": p.nsn,
            "upc": p.upc,
            "unspsc": p.unspsc,

            "hazmat": p.hazmat,
            "product_info_code": p.product_info_code,

            "url_508": p.url_508,
            "product_url": p.product_url,

            "row_signature": p.row_signature,

            "created_time": p.created_time,
            "updated_time": p.updated_time,

            "dim_id": d.dim_id if d else None,

            "length": float(d.length) if d and d.length is not None else None,
            "width": float(d.width) if d and d.width is not None else None,
            "height": float(d.height) if d and d.height is not None else None,

            "physical_uom": d.physical_uom if d else None,

            "weight_lbs": float(d.weight_lbs) if d and d.weight_lbs is not None else None,
            "warranty_period": d.warranty_period if d else None,

            "photo_type": d.photo_type if d else None,
            "photo_path": d.photo_path if d else None,

            "dim_created_time": d.created_time if d else None,
            "dim_updated_time": d.updated_time if d else None,
        })

    return result