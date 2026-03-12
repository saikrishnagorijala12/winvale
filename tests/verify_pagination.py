import pytest
from fastapi.testclient import TestClient

def test_get_all_clients_pagination(client):
    response = client.get("/clients?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "clients" in data
    assert "total_count" in data
    assert "status_counts" in data
    assert len(data["clients"]) <= 5
    # Verify nested contract structure if at least one client has a contract
    for client_data in data["clients"]:
        assert "contract" in client_data

def test_get_all_users_pagination(client):
    response = client.get("/users/all?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total_count" in data
    assert "status_counts" in data
    assert len(data["users"]) <= 5

def test_client_search(client):
    response = client.get("/clients?search=test")
    assert response.status_code == 200
    data = response.json()
    assert "clients" in data
    assert "total_count" in data

def test_user_search(client):
    response = client.get("/users/all?search=test")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total_count" in data

def test_client_status_filter(client):
    response = client.get("/clients?status=pending")
    assert response.status_code == 200
    data = response.json()
    for c in data["clients"]:
        assert c["status"] == "pending"

def test_user_status_filter(client):
    response = client.get("/users/all?status=pending")
    assert response.status_code == 200
    data = response.json()
    for u in data["users"]:
        # The service logic for users: if status is pending, it filters by is_active=False and is_deleted=False
        assert u["is_active"] is False
        assert u["is_deleted"] is False
