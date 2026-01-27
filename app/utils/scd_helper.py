from app.models import ProductHistory


def create_product_history_snapshot(
    product,
    client_id: int,
    *,
    is_current: bool = True,
    end_date=None,
):
    return ProductHistory(
        product_id=product.product_id,
        client_id=client_id,

        item_type=product.item_type,
        manufacturer=product.manufacturer,
        manufacturer_part_number=product.manufacturer_part_number,
        vendor_part_number=product.vendor_part_number,

        sin=product.sin,

        item_name=product.item_name,
        item_description=product.item_description,

        recycled_content_percent=product.recycled_content_percent,

        uom=product.uom,
        quantity_per_pack=product.quantity_per_pack,
        quantity_unit_uom=product.quantity_unit_uom,

        currency=product.currency,
        commercial_price=product.commercial_price,

        mfc_name=product.mfc_name,
        mfc_price=product.mfc_price,

        govt_price_no_fee=product.govt_price_no_fee,
        govt_price_with_fee=product.govt_price_with_fee,

        country_of_origin=product.country_of_origin,

        delivery_days=product.delivery_days,
        lead_time_code=product.lead_time_code,

        fob_us=product.fob_us,
        fob_ak=product.fob_ak,
        fob_hi=product.fob_hi,
        fob_pr=product.fob_pr,

        nsn=product.nsn,
        upc=product.upc,
        unspsc=product.unspsc,

        sale_price_with_fee=product.sale_price_with_fee,

        start_date=product.start_date,
        stop_date=product.stop_date,

        default_photo=product.default_photo,
        photo_2=product.photo_2,
        photo_3=product.photo_3,
        photo_4=product.photo_4,

        product_url=product.product_url,

        warranty_period=product.warranty_period,
        warranty_unit_of_time=product.warranty_unit_of_time,

        length=product.length,
        width=product.width,
        height=product.height,

        physical_uom=product.physical_uom,
        weight_lbs=product.weight_lbs,

        product_info_code=product.product_info_code,
        url_508=product.url_508,

        hazmat=product.hazmat,

        dealer_cost=product.dealer_cost,
        mfc_markup_percentage=product.mfc_markup_percentage,
        govt_markup_percentage=product.govt_markup_percentage,

        row_signature=product.row_signature,

        is_current=is_current,
        effective_end_date=end_date,
    )
