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
from typing import List, Optional
from app.models.modification_action import ModificationAction
from app.models.product_dim import ProductDim


def export_price_modifications_excel(
    db,
    client_id: Optional[int] = None,
    job_id: Optional[int] = None,
    selected_types: Optional[List[str]] = None,
):
    ordered_tabs = [
        ("NEW_PRODUCT", "Additions"),
        ("REMOVED_PRODUCT", "Deletions"),
        ("PRICE_INCREASE", "Price Increase"),
        ("PRICE_DECREASE", "Price Decrease"),
        ("DESCRIPTION_CHANGE", "Description Changes"),
    ]

    all_types = [t[0] for t in ordered_tabs]
    selected_types = [t for t in (selected_types or all_types) if t in all_types]
    if not selected_types:
        selected_types = all_types

    query = (
        db.query(ModificationAction)
        .filter(ModificationAction.action_type.in_(selected_types))
    )

    if client_id is not None:
        query = query.filter(ModificationAction.client_id == client_id)

    if job_id is not None:
        query = query.filter(ModificationAction.job_id == job_id)

    # Optimization: Use .with_entities to fetch raw data instead of full ORM objects.
    # This bypasses the expensive object creation and session tracking overhead.
    query = query.with_entities(
        ModificationAction.action_type, # 0
        ModificationAction.new_price,   # 1
        ModificationAction.old_price,   # 2
        ProductMaster.item_type,        # 3
        ProductMaster.manufacturer,     # 4
        ProductMaster.manufacturer_part_number, # 5
        ProductMaster.vendor_part_number, # 6
        ProductMaster.sin,              # 7
        ProductMaster.item_name,         # 8
        ProductMaster.item_description, # 9
        ProductMaster.recycled_content_percent, # 10
        ProductMaster.uom,              # 11
        ProductMaster.quantity_per_pack, # 12
        ProductMaster.quantity_unit_uom, # 13
        ProductMaster.commercial_price,  # 14
        ProductMaster.mfc_name,          # 15
        ProductMaster.mfc_price,         # 16
        ProductMaster.govt_price_no_fee, # 17
        ProductMaster.govt_price_with_fee, # 18
        ProductMaster.country_of_origin, # 19
        ProductMaster.delivery_days,     # 20
        ProductMaster.lead_time_code,    # 21
        ProductMaster.fob_us,            # 22
        ProductMaster.fob_ak,            # 23
        ProductMaster.fob_hi,            # 24
        ProductMaster.fob_pr,            # 25
        ProductMaster.nsn,               # 26
        ProductMaster.upc,               # 27
        ProductMaster.unspsc,            # 28
        ProductMaster.sale_price_with_fee, # 29
        ProductMaster.start_date,        # 30
        ProductMaster.stop_date,         # 31
        ProductMaster.default_photo,     # 32
        ProductMaster.photo_2,           # 33
        ProductMaster.photo_3,           # 34
        ProductMaster.photo_4,           # 35
        ProductMaster.product_url,       # 36
        ProductMaster.warranty_period,   # 37
        ProductMaster.warranty_unit_of_time, # 38
        ProductMaster.product_info_code, # 39
        ProductMaster.url_508,           # 40
        ProductMaster.hazmat,            # 41
        ProductMaster.dealer_cost,       # 42
        ProductMaster.mfc_markup_percentage, # 43
        ProductMaster.govt_markup_percentage, # 44
        ProductDim.length,               # 45
        ProductDim.width,                # 46
        ProductDim.height,               # 47
        ProductDim.physical_uom,         # 48
        ProductDim.weight_lbs,           # 49
        CPLList.manufacturer_name,       # 50
        CPLList.manufacturer_part_number, # 51
        CPLList.item_name,               # 52
        CPLList.item_description,        # 53
        CPLList.origin_country,          # 54
    ).outerjoin(ProductMaster, ModificationAction.product_id == ProductMaster.product_id)\
     .outerjoin(ProductDim, ProductMaster.product_id == ProductDim.product_id)\
     .outerjoin(CPLList, ModificationAction.cpl_id == CPLList.cpl_id)

    wb = Workbook(write_only=True)

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

    def set_fixed_widths(ws):
        for col in range(1, len(base_headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 18

    def create_sheet(title):
        ws = wb.create_sheet(title)
        # In write_only mode, structural properties must be set before data is appended
        ws.freeze_panes = "D3"
        ws.row_dimensions[1].height = 45
        ws.row_dimensions[2].height = 35

        set_fixed_widths(ws)

        for start, end in merges:
            ws.merged_cells.add(f"{get_column_letter(start)}1:{get_column_letter(end)}1")

        # ---- Row 1 (Section Header) ----
        header_row_1 = []
        for value in group_row:
            cell = WriteOnlyCell(ws, value=value)
            cell.fill = fill_dark
            cell.font = font_white
            cell.alignment = center_align
            cell.border = header_border
            header_row_1.append(cell)
        ws.append(header_row_1)

        # ---- Row 2 (Column Headers) ----
        header_row_2 = []
        for value in base_headers:
            cell = WriteOnlyCell(ws, value=value)
            cell.fill = fill_light
            cell.font = font_standard
            cell.alignment = center_align
            cell.border = header_border
            header_row_2.append(cell)
        ws.append(header_row_2)

        return ws

    selected_types_set = set(selected_types)

    for action_type, title in ordered_tabs:
        if action_type in selected_types_set:
            sheets[action_type] = create_sheet(title)

    for mod in query.yield_per(500):
        # Index-based access is significantly faster than ORM attribute access
        action_type = mod[0]
        ws = sheets.get(action_type)
        if not ws:
            continue

        price = mod[1] if mod[1] is not None else mod[2] # new_price if not None else old_price

        # Pre-check existence for fallback logic
        has_product = mod[3] is not None
        has_cpl = mod[50] is not None # CPL manufacturer_name
        has_dim = mod[45] is not None # ProductDim length

        row = [
            mod[3] if has_product else None, # item_type
            mod[4] if has_product else (mod[50] if has_cpl else None), # manufacturer
            mod[5] if has_product else (mod[51] if has_cpl else None), # manufacturer_part_number
            mod[6] if has_product else None, # vendor_part_number
            mod[7] if has_product else None, # sin
            mod[8] if has_product else (mod[52] if has_cpl else None), # item_name
            mod[9] if has_product else (mod[53] if has_cpl else None), # item_description
            float(mod[10]) if has_product and mod[10] else None, # recycled_content_percent
            mod[11] if has_product else None, # uom
            mod[12] if has_product else None, # quantity_per_pack
            mod[13] if has_product else None, # quantity_unit_uom
            float(price) if price is not None else None, # commercial_price
            mod[15] if has_product else None, # mfc_name
            float(mod[16]) if has_product and mod[16] is not None else None, # mfc_price
            float(mod[17]) if has_product and mod[17] is not None else None, # govt_price_no_fee
            float(mod[18]) if has_product and mod[18] is not None else None, # govt_price_with_fee
            mod[19] if has_product else (mod[54] if has_cpl else None), # country_of_origin
            mod[20] if has_product else None, # delivery_days
            mod[21] if has_product else None, # lead_time_code
            mod[22] if has_product else None, # fob_us
            mod[23] if has_product else None, # fob_ak
            mod[24] if has_product else None, # fob_hi
            mod[25] if has_product else None, # fob_pr
            mod[26] if has_product else None, # nsn
            mod[27] if has_product else None, # upc
            mod[28] if has_product else None, # unspsc
            float(mod[29]) if has_product and mod[29] is not None else None, # sale_price_with_fee
            mod[30] if has_product else None, # start_date
            mod[31] if has_product else None, # stop_date
            mod[32] if has_product else None, # default_photo
            mod[33] if has_product else None, # photo_2
            mod[34] if has_product else None, # photo_3
            mod[35] if has_product else None, # photo_4
            mod[36] if has_product else None, # product_url
            mod[37] if has_product else None, # warranty_period
            mod[38] if has_product else None, # warranty_unit_of_time
            float(mod[45]) if has_dim else None, # length
            float(mod[46]) if has_dim else None, # width
            float(mod[47]) if has_dim else None, # height
            mod[48] if has_dim else None, # physical_uom
            float(mod[49]) if has_dim else None, # weight_lbs
            mod[39] if has_product else None, # product_info_code
            mod[40] if has_product else None, # url_508
            mod[41] if has_product else None, # hazmat
            float(mod[42]) if has_product and mod[42] is not None else None, # dealer_cost
            float(mod[43]) if has_product and mod[43] is not None else None, # mfc_markup_percentage
            float(mod[44]) if has_product and mod[44] is not None else None, # govt_markup_percentage
        ]
        ws.append(row)

    return wb


def export_products_excel(db, client_id: Optional[int] = None):

    query = (
        db.query(ProductMaster)
        .filter(ProductMaster.is_deleted.is_(False))
    )

    if client_id is not None:
        query = query.filter(ProductMaster.client_id == client_id)

    # Optimization: Fetch raw data tuples to bypass ORM overhead
    query = query.with_entities(
        ProductMaster.item_type, # 0
        ProductMaster.manufacturer, # 1
        ProductMaster.manufacturer_part_number, # 2
        ProductMaster.vendor_part_number, # 3
        ProductMaster.sin, # 4
        ProductMaster.item_name, # 5
        ProductMaster.item_description, # 6
        ProductMaster.recycled_content_percent, # 7
        ProductMaster.uom, # 8
        ProductMaster.quantity_per_pack, # 9
        ProductMaster.quantity_unit_uom, # 10
        ProductMaster.commercial_price, # 11
        ProductMaster.mfc_name, # 12
        ProductMaster.mfc_price, # 13
        ProductMaster.govt_price_no_fee, # 14
        ProductMaster.govt_price_with_fee, # 15
        ProductMaster.country_of_origin, # 16
        ProductMaster.delivery_days, # 17
        ProductMaster.lead_time_code, # 18
        ProductMaster.fob_us, # 19
        ProductMaster.fob_ak, # 20
        ProductMaster.fob_hi, # 21
        ProductMaster.fob_pr, # 22
        ProductMaster.nsn, # 23
        ProductMaster.upc, # 24
        ProductMaster.unspsc, # 25
        ProductMaster.sale_price_with_fee, # 26
        ProductMaster.start_date, # 27
        ProductMaster.stop_date, # 28
        ProductMaster.default_photo, # 29
        ProductMaster.photo_2, # 30
        ProductMaster.photo_3, # 31
        ProductMaster.photo_4, # 32
        ProductMaster.product_url, # 33
        ProductMaster.warranty_period, # 34
        ProductMaster.warranty_unit_of_time, # 35
        ProductDim.length, # 36
        ProductDim.width, # 37
        ProductDim.height, # 38
        ProductDim.physical_uom, # 39
        ProductDim.weight_lbs, # 40
        ProductMaster.product_info_code, # 41
        ProductMaster.url_508, # 42
        ProductMaster.hazmat, # 43
        ProductMaster.dealer_cost, # 44
        ProductMaster.mfc_markup_percentage, # 45
        ProductMaster.govt_markup_percentage, # 46
        ClientProfile.company_name, # 47 (client_name)
    ).outerjoin(ProductDim, ProductMaster.product_id == ProductDim.product_id)\
     .outerjoin(ClientProfile, ProductMaster.client_id == ClientProfile.client_id)

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

    merges = [
        (2, 3), (6, 8), (10, 11), (13, 14),
        (15, 16), (18, 23), (27, 29),
        (30, 34), (35, 36), (37, 41),
        (42, 44), (45, 47)
    ]

    # Shift merges if "Client Details" was inserted
    offset = 1 if client_id is None else 0
    adjusted_merges = [(start + offset, end + offset) for start, end in merges]

    total_columns = len(base_headers)

    # In write_only mode, structural properties must be set before data is appended
    ws.freeze_panes = get_column_letter(4 + offset) + "3"
    ws.row_dimensions[1].height = 45
    ws.row_dimensions[2].height = 35

    fill_dark = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    fill_light = PatternFill(start_color="DAE3F3", end_color="DAE3F3", fill_type="solid")

    font_white = Font(name="Calibri", size=11, color="FFFFFF")
    font_standard = Font(name="Calibri", size=11)

    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin = Side(style="thin")
    header_border = Border(top=thin, bottom=thin, left=thin, right=thin)

    for col in range(1, total_columns + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

    for start, end in adjusted_merges:
        ws.merged_cells.add(f"{get_column_letter(start)}1:{get_column_letter(end)}1")

    header_row_1 = []
    for value in group_row:
        cell = WriteOnlyCell(ws, value=value)
        cell.fill = fill_dark
        cell.font = font_white
        cell.alignment = center_align
        cell.border = header_border
        header_row_1.append(cell)

    ws.append(header_row_1)

    header_row_2 = []
    for value in base_headers:
        cell = WriteOnlyCell(ws, value=value)
        cell.fill = fill_light
        cell.font = font_standard
        cell.alignment = center_align
        cell.border = header_border
        header_row_2.append(cell)

    ws.append(header_row_2)

    for mod in query.yield_per(500):
        # Using mod[index] is significantly faster than object access
        has_dim = mod[36] is not None # dimension length

        row = [
            mod[0], # item_type
            mod[1], # manufacturer
            mod[2], # manufacturer_part_number
            mod[3], # vendor_part_number
            mod[4], # sin
            mod[5], # item_name
            mod[6], # item_description
            float(mod[7]) if mod[7] is not None else None, # recycled_content_percent
            mod[8], # uom
            mod[9], # quantity_per_pack
            mod[10], # quantity_unit_uom
            float(mod[11]) if mod[11] else None, # commercial_price
            mod[12], # mfc_name
            float(mod[13]) if mod[13] else None, # mfc_price
            float(mod[14]) if mod[14] else None, # govt_price_no_fee
            float(mod[15]) if mod[15] else None, # govt_price_with_fee
            mod[16], # country_of_origin
            mod[17], # delivery_days
            mod[18], # lead_time_code
            mod[19], # fob_us
            mod[20], # fob_ak
            mod[21], # fob_hi
            mod[22], # fob_pr
            mod[23], # nsn
            mod[24], # upc
            mod[25], # unspsc
            float(mod[26]) if mod[26] else None, # sale_price_with_fee
            mod[27], # start_date
            mod[28], # stop_date
            mod[29], # default_photo
            mod[30], # photo_2
            mod[31], # photo_3
            mod[32], # photo_4
            mod[33], # product_url
            mod[34], # warranty_period
            mod[35], # warranty_unit_of_time
            float(mod[36]) if has_dim else None, # length
            float(mod[37]) if has_dim else None, # width
            float(mod[38]) if has_dim else None, # height
            mod[39] if has_dim else None, # physical_uom
            float(mod[40]) if has_dim else None, # weight_lbs
            mod[41], # product_info_code
            mod[42], # url_508
            mod[43], # hazmat
            float(mod[44]) if mod[44] else None, # dealer_cost
            float(mod[45]) if mod[45] else None, # mfc_markup_percentage
            float(mod[46]) if mod[46] else None, # govt_markup_percentage
        ]

        if client_id is None:
            row.insert(0, mod[47]) # company_name

        ws.append(row)

    return wb


def get_master_filename(db: Session, client_id: Optional[int] = None):
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if client_id is not None:
        client = db.query(ClientProfile).filter_by(client_id=client_id).first()
        if client:
            return f"{client.company_name}_products_{date_str}.xlsx"

    return f"all_products_{date_str}.xlsx"