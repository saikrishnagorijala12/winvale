from sqlalchemy.orm import Session
from app.models.client_profiles import ClientProfile
from app.models.client_contracts import ClientContracts

def get_all_clients(db: Session):
    return db.query(ClientProfile).all()

def get_all_c_contracts(db: Session):
    return db.query(ClientContracts).all()