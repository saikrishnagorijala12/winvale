import pytest
from app.auth.dependencies import get_current_user

@pytest.fixture()
def client_with_admin(client):
    def override_get_current_user():
        return {
            "email": "saikrishnagorijal14@gmail.com",
            "role": "admin"
        }

    from main import app
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client
    app.dependency_overrides.clear()


def test_create_user(client_with_admin):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "phone_no": "9999999999",
        "role_name": "admin"
    }

    response = client_with_admin.post("/users", json=payload)

    assert response.status_code in (201, 409)
