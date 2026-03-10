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
from app.utils.export_constants import (
    PRICE_CHANGE_HEADERS, PRICE_CHANGE_GROUP_ROW, PRICE_CHANGE_MERGES,
    STANDARD_MODIFICATION_HEADERS, STANDARD_MODIFICATION_GROUP_ROW, STANDARD_MODIFICATION_MERGES,
    PRODUCT_EXPORT_HEADERS, PRODUCT_EXPORT_GROUP_ROW, PRODUCT_EXPORT_MERGES
)


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
        .options(
            joinedload(ModificationAction.product).joinedload(ProductMaster.dimension),
            joinedload(ModificationAction.cpl_item)
        )
        .filter(ModificationAction.action_type.in_(selected_types))
    )

    if client_id is not None:
        query = query.filter(ModificationAction.client_id == client_id)

    if job_id is not None:
        query = query.filter(ModificationAction.job_id == job_id)

    wb = Workbook(write_only=True)

    # --- Header Definitions imported from export_constants.py ---
    price_change_headers = PRICE_CHANGE_HEADERS
    price_change_group_row = PRICE_CHANGE_GROUP_ROW
    price_change_merges = PRICE_CHANGE_MERGES

    standard_headers = STANDARD_MODIFICATION_HEADERS
    standard_group_row = STANDARD_MODIFICATION_GROUP_ROW
    standard_merges = STANDARD_MODIFICATION_MERGES

    fill_dark = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    fill_light = PatternFill(start_color="DAE3F3", end_color="DAE3F3", fill_type="solid")

    font_white = Font(name="Calibri", size=11, color="FFFFFF")
    font_standard = Font(name="Calibri", size=11)

    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    thin = Side(style="thin")
    header_border = Border(top=thin, bottom=thin, left=thin, right=thin)

    sheets = {}
    sheet_row_counters = {}

    def set_fixed_widths(ws, headers):
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[get_column_letter(col)].width = 18

    def create_sheet(title, action_type):
        ws = wb.create_sheet(title)
        ws.freeze_panes = "D3"
        ws.row_dimensions[1].height = 45
        ws.row_dimensions[2].height = 35

        is_price_tab = action_type in ["PRICE_INCREASE", "PRICE_DECREASE"]
        h_row_1 = price_change_group_row if is_price_tab else standard_group_row
        h_row_2 = price_change_headers if is_price_tab else standard_headers
        h_merges = price_change_merges if is_price_tab else standard_merges

        set_fixed_widths(ws, h_row_2)

        for start, end in h_merges:
            ws.merged_cells.add(f"{get_column_letter(start)}1:{get_column_letter(end)}1")

        # ---- Row 1 (Section Header) ----
        header_row_1 = []
        for value in h_row_1:
            cell = WriteOnlyCell(ws, value=value)
            cell.fill = fill_dark
            cell.font = font_white
            cell.alignment = center_align
            cell.border = header_border
            header_row_1.append(cell)
        ws.append(header_row_1)

        # ---- Row 2 (Column Headers) ----
        header_row_2 = []
        for value in h_row_2:
            cell = WriteOnlyCell(ws, value=value)
            cell.fill = fill_light
            cell.font = font_standard
            cell.alignment = center_align
            cell.border = header_border
            header_row_2.append(cell)
        ws.append(header_row_2)

        sheet_row_counters[action_type] = 3  # Data starts at row 3
        return ws

    selected_types_set = set(selected_types)

    for action_type, title in ordered_tabs:
        if action_type in selected_types_set:
            sheets[action_type] = create_sheet(title, action_type)

    for mod in query.yield_per(500):

        ws = sheets.get(mod.action_type)
        if not ws:
            continue

        p = mod.product
        cpl = mod.cpl_item
        d = p.dimension if p else None
        is_price_tab = mod.action_type in ["PRICE_INCREASE", "PRICE_DECREASE"]

        if is_price_tab:
            old_price = float(mod.old_price) if mod.old_price is not None else None
            new_price = float(mod.new_price) if mod.new_price is not None else None

            current_row = sheet_row_counters.get(mod.action_type, 3)
            # Formula: IFERROR((NewPrice - OldPrice) / OldPrice, 0)
            # OldPrice is Col L (12), NewPrice is Col M (13)
            formula = f"=IFERROR((M{current_row}-L{current_row})/L{current_row}, 0)"
            
            perc_change_cell = WriteOnlyCell(ws, value=formula)
            perc_change_cell.number_format = "0.00%"

            price_columns = [old_price, new_price, perc_change_cell]
        else:
            price = mod.new_price if mod.new_price is not None else mod.old_price
            price_columns = [float(price) if price is not None else None]

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
        ] + price_columns + [
            p.mfc_name if p else None,
            float(p.mfc_price) if p and p.mfc_price is not None else None,
            float(p.govt_price_no_fee) if p and p.govt_price_no_fee is not None else None,
            float(p.govt_price_with_fee) if p and p.govt_price_with_fee is not None else None,
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
            float(p.sale_price_with_fee) if p and p.sale_price_with_fee is not None else None,
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
            float(p.dealer_cost) if p and p.dealer_cost is not None else None,
            float(p.mfc_markup_percentage) if p and p.mfc_markup_percentage is not None else None,
            float(p.govt_markup_percentage) if p and p.govt_markup_percentage is not None else None,
        ]

        ws.append(row)
        if mod.action_type in sheet_row_counters:
            sheet_row_counters[mod.action_type] += 1

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

    base_headers = PRODUCT_EXPORT_HEADERS[:]
    group_row = PRODUCT_EXPORT_GROUP_ROW[:]

    if client_id is None:
        base_headers.insert(0, "client_name")
        group_row.insert(0, "Client Details")

    merges = PRODUCT_EXPORT_MERGES

    # Shift merges if "Client Details" was inserted
    offset = 1 if client_id is None else 0
    adjusted_merges = [(start + offset, end + offset) for start, end in merges]

    total_columns = len(base_headers)

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
            float(p.recycled_content_percent) if p.recycled_content_percent is not None else None,
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
            float(d.length) if d and d.length is not None else None,
            float(d.width) if d and d.width is not None else None,
            float(d.height) if d and d.height is not None else None,
            d.physical_uom if d else None,
            float(d.weight_lbs) if d and d.weight_lbs is not None else None,
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