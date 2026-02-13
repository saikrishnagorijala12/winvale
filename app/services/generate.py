from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models import (
    Job,
    User,
    ClientContracts,
    ModificationAction
)
 
def get_job_full_details(db: Session, job_id: int, user_email: str):
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
 
    job = (
        db.query(Job)
        .options(
            joinedload(Job.client),
            joinedload(Job.modification_actions)
                .joinedload(ModificationAction.product),
            joinedload(Job.modification_actions)
                .joinedload(ModificationAction.cpl_item),
        )
        .filter(Job.job_id == job_id)
        .first()
    )
 
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
 
    # if job.user_id != user.user_id:
    #     raise HTTPException(status_code=403, detail="Access denied")
 
    contract = (
        db.query(ClientContracts)
        .filter(ClientContracts.client_id == job.client_id)
        .first()
    )
 
    summary = {
        "products_added": 0,
        "products_deleted": 0,
        "description_changed": 0,
        "price_increased": 0,
        "price_decreased": 0,
    }
 
 
    for a in job.modification_actions:
        product_name = None
        mpn = None
 
        if a.product:
            product_name = a.product.item_name
            mpn = a.product.manufacturer_part_number
        elif a.cpl_item:
            product_name = a.cpl_item.item_name
            mpn = a.cpl_item.manufacturer_part_number
 
        if a.action_type == "NEW_PRODUCT":
            summary["products_added"] += 1
 
        if a.action_type == "REMOVED_PRODUCT":
            summary["products_deleted"] += 1
 
        if a.action_type == "DESCRIPTION_CHANGE":
            summary["description_changed"] += 1
 
        if a.action_type == "PRICE_INCREASE":
            summary["price_increased"] += 1
            
        if a.action_type == "PRICE_DECREASE":
            summary["price_decreased"] += 1     
 
    return {
 
        "job_id": job.job_id,
        "client": {
            "client_id": job.client.client_id if job.client else None,
            "company_name": job.client.company_name if job.client else None,
        },
        "client_contract": None if not contract else {
                        "contract_officer_name":contract.contract_officer_name ,
 
            "contract_number": contract.contract_number,
            "discounts":{
             "gsa_proposed_discount":contract.gsa_proposed_discount,
            "q_v_discount":contract.q_v_discount,
            "gsa_proposed_discount": contract.gsa_proposed_discount},
            "delivery":{
            "normal_delivery_time": contract.normal_delivery_time,
            "expedited_delivery_time": contract.expedited_delivery_time},
            "address":{
            "contract_officer_address":contract.contract_officer_address,
            "contract_officer_city":contract.contract_officer_city,
                        "contract_officer_state":contract.contract_officer_state,
                                    "contract_officer_zip":contract.contract_officer_zip},
                                    "other":{
 
            "fob_term": contract.fob_term,
 
            "energy_star_compliance": contract.energy_star_compliance,
           
            "additional_concessions":contract.additional_concessions}
        },
        "modification_summary": summary,
    }