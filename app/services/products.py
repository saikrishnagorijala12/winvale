from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.product_master import ProductMaster
from app.utils.name_to_id import get_status_id_by_name
from sqlalchemy.orm import joinedload
from fastapi.encoders import jsonable_encoder


 
def get_all(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    search: Optional[str] = None,
    client_id: Optional[int] = None,
):
    query = (
        db.query(ProductMaster)
        .join(ClientProfile, ProductMaster.client)
        .filter(
            ClientProfile.is_deleted.is_(False),
            ProductMaster.is_deleted.is_(False),
        )
    )
 
    # Filter by client
    if client_id:
        query = query.filter(ProductMaster.client_id == client_id)
 
    # Search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                ProductMaster.item_name.ilike(search_term),
                ProductMaster.manufacturer.ilike(search_term),
                ProductMaster.manufacturer_part_number.ilike(search_term),
            )
        )
 
    total = query.count()
 
    # Pagination
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
        })
 
    return {
        "total": total,
        "items": result
    }


def get_by_id(db: Session, product_id: int):
    p = (
        db.query(ProductMaster)
        .join(ClientProfile, ProductMaster.client)
        .options(
            joinedload(ProductMaster.client),
            joinedload(ProductMaster.dimension),
        )
        .filter(
            ClientProfile.is_deleted.is_(False),
            ProductMaster.product_id == product_id,
            ProductMaster.is_deleted.is_(False),
        )
        .one_or_none()
    )

    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    d = p.dimension

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



def get_by_client(db: Session, client_id: int):
   

    base_query = (
        db.query(ProductMaster)
        .join(ClientProfile, ProductMaster.client)
        .filter(
            ClientProfile.is_deleted.is_(False),
            ProductMaster.client_id == client_id,
            ProductMaster.is_deleted.is_(False),
        )
    )

    total = base_query.count()

    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No products found for given client",
        )

    products = (
        base_query
        .options(
            joinedload(ProductMaster.client),
            joinedload(ProductMaster.dimension),
        )
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
        })

    return {
        "client_id": client_id,
        "total": total,
        "items": result,
    }

# from fastapi import HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy import select, func
# from app.models.product_master import ProductMaster
# from app.models.product_dim import ProductDim
# from app.models.client_profiles import ClientProfile


# def get_all(db: Session, page: int = 1, page_size: int = 100):

#     base_filter = (
#         ProductMaster.is_deleted.is_(False),
#     )

#     total = db.execute(
#         select(func.count())
#         .select_from(ProductMaster)
#         .where(*base_filter)
#     ).scalar()

#     offset = (page - 1) * page_size
#     total_pages = (total + page_size - 1) // page_size

#     rows = db.execute(
#         select(
#             ProductMaster.product_id,
#             ProductMaster.client_id,
#             ProductMaster.item_type,
#             ProductMaster.item_name,
#             ProductMaster.item_description,
#             ProductMaster.manufacturer,
#             ProductMaster.manufacturer_part_number,
#             ProductMaster.vendor_part_number,
#             ProductMaster.sin,
#             ProductMaster.commercial_price,
#             ProductMaster.country_of_origin,
#             ProductMaster.recycled_content_percent,
#             ProductMaster.uom,
#             ProductMaster.quantity_per_pack,
#             ProductMaster.quantity_unit_uom,
#             ProductMaster.nsn,
#             ProductMaster.upc,
#             ProductMaster.unspsc,
#             ProductMaster.hazmat,
#             ProductMaster.product_info_code,
#             ProductMaster.url_508,
#             ProductMaster.product_url,
#             ProductMaster.row_signature,
#             ProductMaster.created_time,
#             ProductMaster.updated_time,
#             ProductDim.dim_id,
#             ProductDim.length,
#             ProductDim.width,
#             ProductDim.height,
#             ProductDim.physical_uom,
#             ProductDim.weight_lbs,
#             ProductDim.warranty_period,
#             ProductDim.photo_type,
#             ProductDim.photo_path,
#             ProductDim.created_time.label("dim_created_time"),
#             ProductDim.updated_time.label("dim_updated_time"),
#         )
#         .join(ProductDim, ProductDim.product_id == ProductMaster.product_id, isouter=True)
#         .where(*base_filter)
#         .offset(offset)
#         .limit(page_size)
#     ).all()

#     items = []

#     for r in rows:
#         items.append({
#             "product_id": r.product_id,
#             "client_id": r.client_id,
#             "client_name": None,
#             "item_type": r.item_type,
#             "item_name": r.item_name,
#             "item_description": r.item_description,
#             "manufacturer": r.manufacturer,
#             "manufacturer_part_number": r.manufacturer_part_number,
#             "client_part_number": r.vendor_part_number,
#             "sin": r.sin,
#             "commercial_list_price": float(r.commercial_price) if r.commercial_price is not None else None,
#             "country_of_origin": r.country_of_origin,
#             "recycled_content_percent": float(r.recycled_content_percent) if r.recycled_content_percent is not None else None,
#             "uom": r.uom,
#             "quantity_per_pack": r.quantity_per_pack,
#             "quantity_unit_uom": r.quantity_unit_uom,
#             "nsn": r.nsn,
#             "upc": r.upc,
#             "unspsc": r.unspsc,
#             "hazmat": r.hazmat,
#             "product_info_code": r.product_info_code,
#             "url_508": r.url_508,
#             "product_url": r.product_url,
#             "row_signature": r.row_signature,
#             "created_time": r.created_time,
#             "updated_time": r.updated_time,
#             "dim_id": r.dim_id,
#             "length": float(r.length) if r.length is not None else None,
#             "width": float(r.width) if r.width is not None else None,
#             "height": float(r.height) if r.height is not None else None,
#             "physical_uom": r.physical_uom,
#             "weight_lbs": float(r.weight_lbs) if r.weight_lbs is not None else None,
#             "warranty_period": r.warranty_period,
#             "photo_type": r.photo_type,
#             "photo_path": r.photo_path,
#             "dim_created_time": r.dim_created_time,
#             "dim_updated_time": r.dim_updated_time,
#         })

#     return {
#         "total": total,
#         "page": page,
#         "page_size": page_size,
#         "total_pages": total_pages,
#         "items": items,
#     }


# def get_by_client(db: Session, client_id: int, page: int = 1, page_size: int = 100):

#     base_filter = (
#         ProductMaster.client_id == client_id,
#         ProductMaster.is_deleted.is_(False),
#     )

#     total = db.execute(
#         select(func.count())
#         .select_from(ProductMaster)
#         .where(*base_filter)
#     ).scalar()

#     if total == 0:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="No products found for given client",
#         )

#     offset = (page - 1) * page_size
#     total_pages = (total + page_size - 1) // page_size

#     rows = db.execute(
#         select(
#             ProductMaster.product_id,
#             ProductMaster.client_id,
#             ProductMaster.item_type,
#             ProductMaster.item_name,
#             ProductMaster.item_description,
#             ProductMaster.manufacturer,
#             ProductMaster.manufacturer_part_number,
#             ProductMaster.vendor_part_number,
#             ProductMaster.sin,
#             ProductMaster.commercial_price,
#             ProductMaster.country_of_origin,
#             ProductMaster.recycled_content_percent,
#             ProductMaster.uom,
#             ProductMaster.quantity_per_pack,
#             ProductMaster.quantity_unit_uom,
#             ProductMaster.nsn,
#             ProductMaster.upc,
#             ProductMaster.unspsc,
#             ProductMaster.hazmat,
#             ProductMaster.product_info_code,
#             ProductMaster.url_508,
#             ProductMaster.product_url,
#             ProductMaster.row_signature,
#             ProductMaster.created_time,
#             ProductMaster.updated_time,
#             ProductDim.dim_id,
#             ProductDim.length,
#             ProductDim.width,
#             ProductDim.height,
#             ProductDim.physical_uom,
#             ProductDim.weight_lbs,
#             ProductDim.warranty_period,
#             ProductDim.photo_type,
#             ProductDim.photo_path,
#             ProductDim.created_time.label("dim_created_time"),
#             ProductDim.updated_time.label("dim_updated_time"),
#         )
#         .join(ProductDim, ProductDim.product_id == ProductMaster.product_id, isouter=True)
#         .where(*base_filter)
#         .offset(offset)
#         .limit(page_size)
#     ).all()

#     items = []

#     for r in rows:
#         items.append({
#             "product_id": r.product_id,
#             "client_id": r.client_id,
#             "client_name": None,
#             "item_type": r.item_type,
#             "item_name": r.item_name,
#             "item_description": r.item_description,
#             "manufacturer": r.manufacturer,
#             "manufacturer_part_number": r.manufacturer_part_number,
#             "client_part_number": r.vendor_part_number,
#             "sin": r.sin,
#             "commercial_list_price": float(r.commercial_price) if r.commercial_price is not None else None,
#             "country_of_origin": r.country_of_origin,
#             "recycled_content_percent": float(r.recycled_content_percent) if r.recycled_content_percent is not None else None,
#             "uom": r.uom,
#             "quantity_per_pack": r.quantity_per_pack,
#             "quantity_unit_uom": r.quantity_unit_uom,
#             "nsn": r.nsn,
#             "upc": r.upc,
#             "unspsc": r.unspsc,
#             "hazmat": r.hazmat,
#             "product_info_code": r.product_info_code,
#             "url_508": r.url_508,
#             "product_url": r.product_url,
#             "row_signature": r.row_signature,
#             "created_time": r.created_time,
#             "updated_time": r.updated_time,
#             "dim_id": r.dim_id,
#             "length": float(r.length) if r.length is not None else None,
#             "width": float(r.width) if r.width is not None else None,
#             "height": float(r.height) if r.height is not None else None,
#             "physical_uom": r.physical_uom,
#             "weight_lbs": float(r.weight_lbs) if r.weight_lbs is not None else None,
#             "warranty_period": r.warranty_period,
#             "photo_type": r.photo_type,
#             "photo_path": r.photo_path,
#             "dim_created_time": r.dim_created_time,
#             "dim_updated_time": r.dim_updated_time,
#         })

#     return {
#         "client_id": client_id,
#         "total": total,
#         "page": page,
#         "page_size": page_size,
#         "total_pages": total_pages,
#         "items": items,
#     }



# def get_by_id(db: Session, product_id: int):
#     p = (
#         db.query(ProductMaster)
#         .join(ClientProfile, ProductMaster.client)
#         .options(
#             joinedload(ProductMaster.client),
#             joinedload(ProductMaster.dimension),
#         )
#         .filter(
#             ClientProfile.is_deleted.is_(False),
#             ProductMaster.product_id == product_id,
#             ProductMaster.is_deleted.is_(False),
#         )
#         .one_or_none()
#     )

#     if not p:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Product not found",
#         )

#     d = p.dimension

#     return {
#         "product_id": p.product_id,
#         "client_id": p.client_id,
#         "client_name": p.client.company_name if p.client else None,

#         "item_type": p.item_type,
#         "item_name": p.item_name,
#         "item_description": p.item_description,

#         "manufacturer": p.manufacturer,
#         "manufacturer_part_number": p.manufacturer_part_number,
#         "client_part_number": p.vendor_part_number,

#         "sin": p.sin,
#         "commercial_list_price": float(p.commercial_price) if p.commercial_price is not None else None,

#         "country_of_origin": p.country_of_origin,
#         "recycled_content_percent": float(p.recycled_content_percent) if p.recycled_content_percent is not None else None,

#         "uom": p.uom,
#         "quantity_per_pack": p.quantity_per_pack,
#         "quantity_unit_uom": p.quantity_unit_uom,

#         "nsn": p.nsn,
#         "upc": p.upc,
#         "unspsc": p.unspsc,

#         "hazmat": p.hazmat,
#         "product_info_code": p.product_info_code,

#         "url_508": p.url_508,
#         "product_url": p.product_url,

#         "row_signature": p.row_signature,

#         "created_time": p.created_time,
#         "updated_time": p.updated_time,

#         "dim_id": d.dim_id if d else None,
#         "length": float(d.length) if d and d.length is not None else None,
#         "width": float(d.width) if d and d.width is not None else None,
#         "height": float(d.height) if d and d.height is not None else None,
#         "physical_uom": d.physical_uom if d else None,
#         "weight_lbs": float(d.weight_lbs) if d and d.weight_lbs is not None else None,
#         "warranty_period": d.warranty_period if d else None,
#         "photo_type": d.photo_type if d else None,
#         "photo_path": d.photo_path if d else None,
#         "dim_created_time": d.created_time if d else None,
#         "dim_updated_time": d.updated_time if d else None,
#     }


