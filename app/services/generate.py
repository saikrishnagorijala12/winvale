from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models import (
    Job,
    User,
    ClientContracts,
    ModificationAction
)
from app.schemas.generate import JobFullDetailsRead
 
def group_sins_into_ranges(sin_set):
    if not sin_set:
        return []
    return sorted({str(sin).strip() for sin in sin_set if sin})
 
def get_job_full_details(db: Session, job_id: int, user_email: str) -> JobFullDetailsRead:
 
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
 
    job = (
        db.query(Job)
        .options(
            joinedload(Job.client),
            joinedload(Job.modification_actions).joinedload(ModificationAction.product),
            joinedload(Job.modification_actions).joinedload(ModificationAction.cpl_item),
        )
        .filter(Job.job_id == job_id)
        .first()
    )
 
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
 
    contract = (
        db.query(ClientContracts)
        .filter(ClientContracts.client_id == job.client_id)
        .first()
    )
 
    action_map = {
        "NEW_PRODUCT": "products_added",
        "REMOVED_PRODUCT": "products_deleted",
        "DESCRIPTION_CHANGE": "description_changed",
        "PRICE_INCREASE": "price_increased",
        "PRICE_DECREASE": "price_decreased",
    }
 
    summary = {v: 0 for v in action_map.values()}
 
    sin_by_action = {}
    countries_of_origin = set()
 
    price_increase_changes = []
    price_decrease_changes = []
 
    for a in job.modification_actions:
 
        if a.action_type in action_map:
            summary[action_map[a.action_type]] += 1
 
        old_price = a.old_price
        new_price = a.new_price
 
        if old_price is not None and new_price is not None and old_price != 0:
 
            percent_change = round(((new_price - old_price) / old_price) * 100, 2)
 
            if a.action_type == "PRICE_INCREASE":
                price_increase_changes.append(percent_change)
 
            elif a.action_type == "PRICE_DECREASE":
                price_decrease_changes.append(abs(percent_change))
 
        p = a.product
        cpl = a.cpl_item
        country = p.country_of_origin if p else (cpl.origin_country if cpl else None)
        if country:
            countries_of_origin.add(country)
        if p and p.sin:
            sin_by_action.setdefault(a.action_type, set()).add(p.sin)
 
    increase_min = min(price_increase_changes) if price_increase_changes else None
    increase_max = max(price_increase_changes) if price_increase_changes else None
 
    decrease_min = min(price_decrease_changes) if price_decrease_changes else None
    decrease_max = max(price_decrease_changes) if price_decrease_changes else None
 
    grouped_sins_by_action = {}
    total_unique_sins = set()
 
    for action_type, sins in sin_by_action.items():
        grouped_sins_by_action[action_type] = group_sins_into_ranges(sins)
        total_unique_sins.update(sins)
 
    return JobFullDetailsRead.model_validate({
        "job_id": job.job_id,
 
        "client": {
            "client_id": job.client.client_id if job.client else None,
            "company_name": job.client.company_name if job.client else None,
            "logo": job.client.company_logo_url if job.client else None,
        },
 
        "negotiators": [
            {"name": n.name, "title": n.title} for n in job.client.negotiators
        ] if job.client else [],
 
        "client_contract": None if not contract else {
            "contract_officer_name": contract.contract_officer_name,
            "contract_number": contract.contract_number,
            "discounts": {
                "gsa_proposed_discount": contract.gsa_proposed_discount,
                "q_v_discount": contract.q_v_discount,
            },
            "delivery": {
                "normal_delivery_time": contract.normal_delivery_time,
                "expedited_delivery_time": contract.expedited_delivery_time
            },
            "address": {
                "contract_officer_address": contract.contract_officer_address,
                "contract_officer_city": contract.contract_officer_city,
                "contract_officer_state": contract.contract_officer_state,
                "contract_officer_zip": contract.contract_officer_zip
            },
            "other": {
                "fob_term": contract.fob_term,
                "energy_star_compliance": contract.energy_star_compliance,
                "additional_concessions": contract.additional_concessions,
                "epa_method_mechanism": contract.epa_method_mechanism,
                "is_hazardous": contract.is_hazardous
            }
        },
 
        "modification_summary": summary,
        "sin_groups_by_action": grouped_sins_by_action,
        "total_sins": len(total_unique_sins),
 
        "percentage": {
            "price_increase": {
                "min": increase_min,
                "max": increase_max
            },
            "price_decrease": {
                "min": decrease_min,
                "max": decrease_max
            }
        },
 
        "countries_of_origin": list(countries_of_origin)
    })