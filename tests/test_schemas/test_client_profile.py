import pytest
from pydantic import ValidationError
from app.schemas.client_profile import ClientProfileCreate, ClientProfileUpdate

def test_client_profile_create_success():
    payload = {
        "company_name": "Test Company",
        "company_email": "test@company.com",
        "company_phone_no": "1234567890",
        "company_address": "123 Test St",
        "company_city": "Test City",
        "company_state": "TS",
        "company_zip": "12345",
        "status": "pending",
        "negotiators": []
    }
    client = ClientProfileCreate(**payload)
    assert client.company_name == "Test Company"
    assert client.company_email == "test@company.com"

def test_client_profile_create_invalid_email():
    payload = {
        "company_name": "Test Company",
        "company_email": "invalid-email",
        "company_phone_no": "1234567890",
        "company_address": "123 Test St",
        "company_city": "Test City",
        "company_state": "TS",
        "company_zip": "12345",
        "status": "pending"
    }
    with pytest.raises(ValidationError):
        ClientProfileCreate(**payload)

def test_client_profile_update_normalize_empty_to_none():
    payload = {
        "company_name": "  ", # Should become None
        "company_city": "New City"
    }
    update = ClientProfileUpdate(**payload)
    assert update.company_name is None
    assert update.company_city == "New City"

def test_client_profile_create_normalize_email_empty():
    payload = {
        "company_name": "Test Company",
        "company_email": "  ", # Should trigger validation error because it's required in Create
        "company_phone_no": "1234567890",
        "company_address": "123 Test St",
        "company_city": "Test City",
        "company_state": "TS",
        "company_zip": "12345",
        "status": "pending"
    }
    with pytest.raises(ValidationError):
        ClientProfileCreate(**payload)
