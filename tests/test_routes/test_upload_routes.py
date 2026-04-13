"""
Tests for /upload endpoints.

Covers the single POST /upload/{client_id} route — file validation,
background task dispatch, and auth checks.
"""

import pytest
from unittest.mock import patch, ANY, MagicMock
from tests.conftest import FAKE_ADMIN_USER
from io import BytesIO
from fastapi import status


class TestUploadProducts:

    def _xlsx_file(self, filename="products.xlsx"):
        """Return a tuple suitable for the `files` kwarg of TestClient."""
        return ("file", (filename, BytesIO(b"\x00" * 100), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))

    def test_success_returns_202(self, client):
        """Valid .xlsx upload should be accepted immediately."""
        with patch("app.routes.upload.run_upload_background") as mock_service:
            resp = client.post("/upload/1", files=[self._xlsx_file()])
        assert resp.status_code == status.HTTP_202_ACCEPTED
        data = resp.json()
        assert data["status"] == "processing"
        assert "started" in data["message"].lower()
        mock_service.assert_called_once_with(ANY, 1, ANY, ANY, FAKE_ADMIN_USER["email"])

    def test_wrong_file_extension_csv(self, client):
        resp = client.post(
            "/upload/1",
            files=[("file", ("data.csv", BytesIO(b"a,b,c"), "text/csv"))],
        )
        assert resp.status_code == 400
        assert "xlsx" in resp.json()["detail"].lower()

    def test_wrong_file_extension_pdf(self, client):
        resp = client.post(
            "/upload/1",
            files=[("file", ("doc.pdf", BytesIO(b"%PDF"), "application/pdf"))],
        )
        assert resp.status_code == 400

    def test_no_file_attached(self, client):
        resp = client.post("/upload/1")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.post(
            "/upload/1",
            files=[("file", ("products.xlsx", BytesIO(b"\x00"), "application/octet-stream"))],
        )
        assert resp.status_code in (401, 403)

    def test_response_content_type(self, client):
        with patch("app.routes.upload.run_upload_background") as mock_service:
            resp = client.post("/upload/1", files=[self._xlsx_file()])
        assert "application/json" in resp.headers["content-type"]
        mock_service.assert_called_once_with(ANY, 1, ANY, ANY, FAKE_ADMIN_USER["email"])


class TestUploadStatus:

    def test_get_status_success(self, client):
        with patch("app.routes.upload._get_upload_status") as mock_service:
            mock_service.return_value = {"client_id": 1, "status": "completed", "total_count": 10}
            resp = client.get("/upload/1/status")
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"
        mock_service.assert_called_once_with(1)

    def test_get_status_not_found(self, client):
        with patch("app.routes.upload._get_upload_status", return_value=None):
            resp = client.get("/upload/1/status")
        assert resp.status_code == 404

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/upload/1/status")
        assert resp.status_code in (401, 403)


class TestResetUpload:

    def test_reset_success(self, client):
        with patch("app.routes.upload.redis_client") as mock_redis:
            resp = client.post("/upload/1/reset")
        assert resp.status_code == 200
        assert resp.json()["status"] == "reset"
        mock_redis.delete.assert_called_once()

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.post("/upload/1/reset")
        assert resp.status_code in (401, 403)
