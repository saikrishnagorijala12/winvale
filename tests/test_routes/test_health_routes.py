
class TestHealthCheck:

    def test_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_ok_payload(self, client):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}

    def test_no_auth_required(self, unauth_client):
        """Health endpoint should work even without a valid token."""
        response = unauth_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_content_type_is_json(self, client):
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]

    def test_cache_health(self, client):
        response = client.get("/health/cache")
        assert response.status_code == 200
        assert "latency_ms" in response.json()

    def test_db_latency(self, client, mock_db):
        # We need to mock the DB execution for latency check
        mock_db.execute().scalar.return_value = 1
        response = client.get("/health/db-latency")
        assert response.status_code == 200
        assert "latency_ms" in response.json()
