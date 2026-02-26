from collections import defaultdict
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from openpyxl import Workbook
from app.models.product_master import ProductMaster
from app.models.client_profiles import ClientProfile
from app.models.cpl_list import CPLList
from datetime import datetime, timezone
from typing import Optional
from app.models.modification_action import ModificationAction


def export_price_modifications_excel(
    db,
    client_id: Optional[int] = None,
    job_id: Optional[int] = None
):
    query = (
        db.query(ModificationAction)
        .options(
            joinedload(ModificationAction.product).joinedload(ProductMaster.dimension),
            joinedload(ModificationAction.cpl_item)
        )
        .filter(
            ModificationAction.action_type.in_([
                "NEW_PRODUCT",
                "REMOVED_PRODUCT",
                "PRICE_INCREASE",
                "PRICE_DECREASE",
                "DESCRIPTION_CHANGE"
            ])
        )
    )

    if client_id is not None:
        query = query.filter(ModificationAction.client_id == client_id)

    if job_id is not None:
        query = query.filter(ModificationAction.job_id == job_id)

    wb = Workbook()
    wb.remove(wb.active)

    ordered_tabs = [
        ("NEW_PRODUCT", "Additions"),
        ("REMOVED_PRODUCT", "Deletions"),
        ("PRICE_INCREASE", "Price Increase"),
        ("PRICE_DECREASE", "Price Decrease"),
        ("DESCRIPTION_CHANGE", "Description Changes"),
    ]

    base_headers = [
        "item_type", "manufacturer", "manufacturer_part_number",
        "vendor_part_number", "sin", "item_name", "item_description",
        "recycled_content_percent", "uom", "quantity_per_pack",
        "quantity_unit_uom", "commercial_price", "mfc_name", "mfc_price",
        "govt_price_no_fee", "govt_price_with_fee", "country_of_origin",
        "delivery_days", "lead_time_code", "fob_us", "fob_ak",
        "fob_hi", "fob_pr", "nsn", "upc", "unspsc",
        "sale_price_with_fee", "start_date", "stop_date",
        "default_photo", "photo_2", "photo_3", "photo_4",
        "product_url", "warranty_period", "warranty_unit_of_time",
        "length", "width", "height", "physical_uom", "weight_lbs",
        "product_info_code", "url_508", "hazmat",
        "dealer_cost", "mfc_markup_percentage",
        "govt_markup_percentage",
    ]

    group_row = [
        "Base Product or Accessory",
        "Manufacturer Information", "",
        "Vendor Part Number",
        "Special Item Number",
        "Product Information", "", "",
        "Unit of Measure",
        "Quantity Per Pack", "",
        "Commercial Price / MSRP",
        "Most Favored Customer", "",
        "Price Proposal", "",
        "Country of Origin",
        "Delivery Information", "", "", "", "", "",
        "National Stock Number",
        "UPC",
        "UNSPSC",
        "Temporary Price Reduction (TPR)", "", "",
        "Photo File References", "", "", "", "",
        "Warranty Duration", "",
        "Product Dimensions", "", "", "", "",
        "Product Information", "", "",
        "Dealer Markup", "", ""
    ]

    merges = [
        (2, 3), (6, 8), (10, 11), (13, 14),
        (15, 16), (18, 23), (27, 29),
        (30, 34), (35, 36), (37, 41),
        (42, 44), (45, 47)
    ]

    fill_dark = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    fill_light = PatternFill(start_color="DAE3F3", end_color="DAE3F3", fill_type="solid")

    font_white = Font(name="Calibri", size=11, color="FFFFFF")
    font_standard = Font(name="Calibri", size=11)

    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    thin = Side(style="thin")
    header_border = Border(top=thin, bottom=thin, left=thin, right=thin)

    sheets = {}
    width_tracker = {}

    def create_sheet(title):
        ws = wb.create_sheet(title)
        width_tracker[title] = [len(h) for h in base_headers]

        # ---- Row 1 (Section Header) ----
        ws.append(group_row)

        for col in range(1, len(base_headers) + 1):
            cell = ws.cell(row=1, column=col)
            cell.fill = fill_dark
            cell.font = font_white
            cell.alignment = center_align
            cell.border = header_border

        for start, end in merges:
            ws.merge_cells(start_row=1, start_column=start, end_row=1, end_column=end)

        ws.row_dimensions[1].height = 45

        # ---- Row 2 (Column Headers) ----
        ws.append(base_headers)

        for col in range(1, len(base_headers) + 1):
            cell = ws.cell(row=2, column=col)
            cell.fill = fill_light
            cell.font = font_standard
            cell.alignment = center_align
            cell.border = header_border

        ws.row_dimensions[2].height = 35
        ws.freeze_panes = "D3"

        return ws

    for action_type, title in ordered_tabs:
        sheets[action_type] = create_sheet(title)

    for mod in query.yield_per(500):

        ws = sheets.get(mod.action_type)
        if not ws:
            continue

        p = mod.product
        cpl = mod.cpl_item
        d = p.dimension if p else None
        price = mod.new_price if mod.new_price is not None else mod.old_price

        row = [
            p.item_type if p else None,
            p.manufacturer if p else (cpl.manufacturer_name if cpl else None),
            p.manufacturer_part_number if p else (cpl.manufacturer_part_number if cpl else None),
            p.vendor_part_number if p else None,
            p.sin if p else None,
            p.item_name if p else (cpl.item_name if cpl else None),
            p.item_description if p else (cpl.item_description if cpl else None),
            float(p.recycled_content_percent) if p and p.recycled_content_percent else None,
            p.uom if p else None,
            p.quantity_per_pack if p else None,
            p.quantity_unit_uom if p else None,
            float(price) if price else None,
            p.mfc_name if p else None,
            float(p.mfc_price) if p and p.mfc_price else None,
            float(p.govt_price_no_fee) if p and p.govt_price_no_fee else None,
            float(p.govt_price_with_fee) if p and p.govt_price_with_fee else None,
            p.country_of_origin if p else (cpl.origin_country if cpl else None),
            p.delivery_days if p else None,
            p.lead_time_code if p else None,
            p.fob_us if p else None,
            p.fob_ak if p else None,
            p.fob_hi if p else None,
            p.fob_pr if p else None,
            p.nsn if p else None,
            p.upc if p else None,
            p.unspsc if p else None,
            float(p.sale_price_with_fee) if p and p.sale_price_with_fee else None,
            p.start_date if p else None,
            p.stop_date if p else None,
            p.default_photo if p else None,
            p.photo_2 if p else None,
            p.photo_3 if p else None,
            p.photo_4 if p else None,
            p.product_url if p else None,
            p.warranty_period if p else None,
            p.warranty_unit_of_time if p else None,
            float(d.length) if d and d.length else None,
            float(d.width) if d and d.width else None,
            float(d.height) if d and d.height else None,
            d.physical_uom if d else None,
            float(d.weight_lbs) if d and d.weight_lbs else None,
            p.product_info_code if p else None,
            p.url_508 if p else None,
            p.hazmat if p else None,
            float(p.dealer_cost) if p and p.dealer_cost else None,
            float(p.mfc_markup_percentage) if p and p.mfc_markup_percentage else None,
            float(p.govt_markup_percentage) if p and p.govt_markup_percentage else None,
        ]

        ws.append(row)

        # Track column widths
        widths = width_tracker[ws.title]
        for i, value in enumerate(row):
            if value is not None:
                widths[i] = max(widths[i], len(str(value)))

    for title, widths in width_tracker.items():
        ws = wb[title]
        for i, width in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(i)].width = min(width + 2, 50)

    return wb


def export_products_excel(db, client_id: Optional[int] = None):

    query = (
        db.query(ProductMaster)
        .options(
            joinedload(ProductMaster.dimension),
            joinedload(ProductMaster.client)
        )
        .filter(ProductMaster.is_deleted.is_(False))
    )

    if client_id is not None:
        query = query.filter(ProductMaster.client_id == client_id)

    wb = Workbook(write_only=True)
    ws = wb.create_sheet("PRODUCTS")

    base_headers = [
        "item_type", "manufacturer", "manufacturer_part_number",
        "vendor_part_number", "sin", "item_name", "item_description",
        "recycled_content_percent", "uom", "quantity_per_pack",
        "quantity_unit_uom", "commercial_price", "mfc_name", "mfc_price",
        "govt_price_no_fee", "govt_price_with_fee", "country_of_origin",
        "delivery_days", "lead_time_code", "fob_us", "fob_ak",
        "fob_hi", "fob_pr", "nsn", "upc", "unspsc",
        "sale_price_with_fee", "start_date", "stop_date",
        "default_photo", "photo_2", "photo_3", "photo_4",
        "product_url", "warranty_period", "warranty_unit_of_time",
        "length", "width", "height", "physical_uom", "weight_lbs",
        "product_info_code", "url_508", "hazmat",
        "dealer_cost", "mfc_markup_percentage",
        "govt_markup_percentage",
    ]

    group_row = [
        "Base Product or Accessory",
        "Manufacturer Information", "",
        "Vendor Part Number",
        "Special Item Number",
        "Product Information", "", "",
        "Unit of Measure",
        "Quantity Per Pack", "",
        "Commercial Price / MSRP",
        "Most Favored Customer", "",
        "Price Proposal", "",
        "Country of Origin",
        "Delivery Information", "", "", "", "", "",
        "National Stock Number",
        "UPC",
        "UNSPSC",
        "Temporary Price Reduction (TPR)", "", "",
        "Photo File References", "", "", "", "",
        "Warranty Duration", "",
        "Product Dimensions", "", "", "", "",
        "Product Information / Categorization", "", "",
        "Dealer Markup", "", ""
    ]

    if client_id is None:
        base_headers.insert(0, "client_name")
        group_row.insert(0, "Client Details")

    total_columns = len(base_headers)
    if client_id is None:
        total_columns += 1

    for col in range(1, total_columns + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    ws.sheet_format.defaultRowHeight = 20

    fill_dark = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    fill_light = PatternFill(start_color="DAE3F3", end_color="DAE3F3", fill_type="solid")

    font_white = Font(name="Calibri", size=12, color="FFFFFF")
    font_standard = Font(name="Calibri", size=12)

    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    header_row_1 = []
    for value in group_row:
        cell = WriteOnlyCell(ws, value=value)
        cell.fill = fill_dark
        cell.font = font_white
        cell.alignment = center_align
        header_row_1.append(cell)

    ws.append(header_row_1)

    header_row_2 = []
    for value in base_headers:
        cell = WriteOnlyCell(ws, value=value)
        cell.fill = fill_light
        cell.font = font_standard
        cell.alignment = center_align
        header_row_2.append(cell)

    ws.append(header_row_2)

    for p in query.yield_per(500):

        d = p.dimension

        row = [
            p.item_type,
            p.manufacturer,
            p.manufacturer_part_number,
            p.vendor_part_number,
            p.sin,
            p.item_name,
            p.item_description,
            float(p.recycled_content_percent) if p.recycled_content_percent else None,
            p.uom,
            p.quantity_per_pack,
            p.quantity_unit_uom,
            float(p.commercial_price) if p.commercial_price else None,
            p.mfc_name,
            float(p.mfc_price) if p.mfc_price else None,
            float(p.govt_price_no_fee) if p.govt_price_no_fee else None,
            float(p.govt_price_with_fee) if p.govt_price_with_fee else None,
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
            float(p.sale_price_with_fee) if p.sale_price_with_fee else None,
            p.start_date,
            p.stop_date,
            p.default_photo,
            p.photo_2,
            p.photo_3,
            p.photo_4,
            p.product_url,
            p.warranty_period,
            p.warranty_unit_of_time,
            float(d.length) if d and d.length else None,
            float(d.width) if d and d.width else None,
            float(d.height) if d and d.height else None,
            d.physical_uom if d else None,
            float(d.weight_lbs) if d and d.weight_lbs else None,
            p.product_info_code,
            p.url_508,
            p.hazmat,
            float(p.dealer_cost) if p.dealer_cost else None,
            float(p.mfc_markup_percentage) if p.mfc_markup_percentage else None,
            float(p.govt_markup_percentage) if p.govt_markup_percentage else None,
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