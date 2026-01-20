from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.product_master import ProductMaster
from app.utils.name_to_id import get_status_id_by_name


def get_all(db: Session):
    products = (
        db.query(ProductMaster)
        .all()
    )

    # if not products:
    #     raise HTTPException(
    #         status_code=status.HTTP_301_MOVED_PERMANENTLY,
    #         detail="No Products found"
    #     )
 
    return [
    {
        "product_id": p.product_id,
        "client": p.client.company_name,

        "item_type": p.item_type,
        "item_name": p.item_name,
        "item_description": p.item_description,

        "manufacturer": p.manufacturer,
        "manufacturer_part_number": p.manufacturer_part_number,
        "client_part_number": p.client_part_number,

        "sin": p.sin,
        "commercial_list_price": float(p.commercial_list_price) if p.commercial_list_price else None,

        "country_of_origin": p.country_of_origin,
        "recycled_content_percent": float(p.recycled_content_percent) if p.recycled_content_percent else None,

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

        # "row_signature": p.row_signature,
        "created_time": p.created_time,
        "updated_time": p.updated_time,
    }
    for p in products
]


def get_by_id(db: Session, product_id: int):
    product = (
        db.query(ProductMaster)
        .filter(ProductMaster.product_id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return {
        "product_id": product.product_id,
        "client": product.client.company_name,

        "item_type": product.item_type,
        "item_name": product.item_name,
        "item_description": product.item_description,

        "manufacturer": product.manufacturer,
        "manufacturer_part_number": product.manufacturer_part_number,
        "client_part_number": product.client_part_number,

        "sin": product.sin,
        "commercial_list_price": float(product.commercial_list_price)
        if product.commercial_list_price else None,

        "country_of_origin": product.country_of_origin,
        "recycled_content_percent": float(product.recycled_content_percent)
        if product.recycled_content_percent else None,

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

        "created_time": product.created_time,
        "updated_time": product.updated_time,
    }

def get_by_client(db: Session, client_id: int):
    products = (
        db.query(ProductMaster)
        .filter(ProductMaster.client_id == client_id)
        .all()
    )

    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Product found for given user"
        )
 
    return [
    {
        "product_id": p.product_id,
        "client": p.client.company_name,

        "item_type": p.item_type,
        "item_name": p.item_name,
        "item_description": p.item_description,

        "manufacturer": p.manufacturer,
        "manufacturer_part_number": p.manufacturer_part_number,
        "client_part_number": p.client_part_number,

        "sin": p.sin,
        "commercial_list_price": float(p.commercial_list_price) if p.commercial_list_price else None,

        "country_of_origin": p.country_of_origin,
        "recycled_content_percent": float(p.recycled_content_percent) if p.recycled_content_percent else None,

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

        # "row_signature": p.row_signature,
        "created_time": p.created_time,
        "updated_time": p.updated_time,
    }
    for p in products
]