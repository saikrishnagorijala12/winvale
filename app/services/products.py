from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from app.models.client_profiles import ClientProfile
from app.models.product_master import ProductMaster


def _serialize_product(p, d) -> dict:
    return {
        "product_id": p.product_id,
        "client_id": p.client_id,
        "client_name": p.client.company_name if p.client else None,
        "item_type": p.item_type,
        "item_name": p.item_name,
        "item_description": p.item_description,
        "manufacturer": p.manufacturer,
        "manufacturer_part_number": p.manufacturer_part_number,
        "client_part_number": p.vendor_part_number,
        "sin": p.sin,
        "commercial_list_price": float(p.commercial_price) if p.commercial_price is not None else None,
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
    }


def _base_query(db: Session):
    return (
        db.query(ProductMaster)
        .join(ClientProfile, ProductMaster.client)
        .filter(
            ClientProfile.is_deleted.is_(False),
            ProductMaster.is_deleted.is_(False),
        )
    )


def get_all(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    client_id: Optional[int] = None,
):
    query = _base_query(db)

    if client_id:
        query = query.filter(ProductMaster.client_id == client_id)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                ProductMaster.item_name.ilike(term),
                ProductMaster.manufacturer.ilike(term),
                ProductMaster.manufacturer_part_number.ilike(term),
            )
        )

    total = query.count()
    offset = (page - 1) * page_size

    products = (
        query
        .options(
            joinedload(ProductMaster.client),
            joinedload(ProductMaster.dimension),
        )
        .order_by(ProductMaster.created_time.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "items": [_serialize_product(p, p.dimension) for p in products],
    }


def get_by_id(db: Session, product_id: int):
    p = (
        _base_query(db)
        .options(
            joinedload(ProductMaster.client),
            joinedload(ProductMaster.dimension),
        )
        .filter(ProductMaster.product_id == product_id)
        .one_or_none()
    )

    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return _serialize_product(p, p.dimension)


def get_by_client(
    db: Session, 
    client_id: int,
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None
):
    query = _base_query(db).filter(ProductMaster.client_id == client_id)
    
    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                ProductMaster.item_name.ilike(term),
                ProductMaster.manufacturer.ilike(term),
                ProductMaster.manufacturer_part_number.ilike(term),
            )
        )
        
    total = query.count()
    offset = (page - 1) * page_size

    products = (
        query
        .options(
            joinedload(ProductMaster.client),
            joinedload(ProductMaster.dimension),
        )
        .order_by(ProductMaster.created_time.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return {
        "client_id": client_id,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
        "items": [_serialize_product(p, p.dimension) for p in products],
    }
