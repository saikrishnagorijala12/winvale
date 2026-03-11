from typing import Optional, Dict, List
from .base import ORMBase

class ClientInfo(ORMBase):
    client_id: Optional[int] = None
    company_name: Optional[str] = None
    logo: Optional[str] = None

class NegotiatorInfo(ORMBase):
    name: Optional[str] = None

class DiscountInfo(ORMBase):
    gsa_proposed_discount: Optional[float] = None
    q_v_discount: Optional[str] = None

class DeliveryInfo(ORMBase):
    normal_delivery_time: Optional[int] = None
    expedited_delivery_time: Optional[int] = None

class AddressInfo(ORMBase):
    contract_officer_address: Optional[str] = None
    contract_officer_city: Optional[str] = None
    contract_officer_state: Optional[str] = None
    contract_officer_zip: Optional[str] = None

class OtherContractInfo(ORMBase):
    fob_term: Optional[str] = None
    energy_star_compliance: Optional[str] = None
    additional_concessions: Optional[str] = None

class ClientContractInfo(ORMBase):
    contract_officer_name: Optional[str] = None
    contract_number: Optional[str] = None
    discounts: DiscountInfo
    delivery: DeliveryInfo
    address: AddressInfo
    other: OtherContractInfo

class ModificationSummary(ORMBase):
    products_added: int
    products_deleted: int
    description_changed: int
    price_increased: int
    price_decreased: int

class PriceRange(ORMBase):
    min: float | None
    max: float | None
 
 
class Percentage(ORMBase):
    price_increase: PriceRange
    price_decrease: PriceRange

class JobFullDetailsRead(ORMBase):
    job_id: int
    client: ClientInfo
    negotiator: NegotiatorInfo
    client_contract: Optional[ClientContractInfo] = None
    modification_summary: ModificationSummary
    sin_groups_by_action: Dict[str, List[str]]
    total_sins: int
    percentage: Percentage
    countries_of_origin: List[str]

