def test_create_user(client):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "phone_no": "9999999999",
        "role_id": 1
    }

    response = client.post("/users", json=payload)

    assert response.status_code in (200, 201, 409)