import pytest
from unittest.mock import patch, ANY
from io import BytesIO
from fastapi import status, HTTPException
from tests.conftest import FAKE_ADMIN_USER


class TestUploadCPL:
    """POST /cpl/{id} — upload a price list .xlsx."""

    def _xlsx_file(self, filename="cpl.xlsx"):
        return ("files", (filename, BytesIO(b"\x00" * 100), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))

    def test_success(self, client, mock_db):
        fake_result = {
            "job_id": 10,
            "client_id": 5,
            "status": "pending",
            "summary": {
                "new_products": 3,
                "removed_products": 1,
                "price_increase": 2,
                "price_decrease": 0,
                "description_changed": 1,
                "name_changed": 0,
                "no_change": 5,
            },
            "next_step": "Approve or reject job",
        }
        with patch("app.routes.pricelist._get_product_upload_payload", return_value={"status": "completed"}):
            with patch("app.routes.pricelist.upload_cpl_service", return_value=fake_result) as mock_service:
                resp = client.post("/cpl/5", files=[self._xlsx_file()])
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == 10
        assert "summary" in data
        mock_service.assert_called_once_with(
            db=mock_db,
            client_id=5,
            files=ANY,
            user_email=FAKE_ADMIN_USER["email"]
        )

    def test_wrong_file_extension_csv(self, client):
        resp = client.post(
            "/cpl/5",
            files=[("files", ("data.csv", BytesIO(b"a,b"), "text/csv"))],
        )
        assert resp.status_code == 400
        assert "xlsx" in resp.json()["detail"].lower()

    def test_wrong_file_extension_txt(self, client):
        resp = client.post(
            "/cpl/5",
            files=[("files", ("data.txt", BytesIO(b"hello"), "text/plain"))],
        )
        assert resp.status_code == 400

    def test_no_file_attached(self, client):
        resp = client.post("/cpl/5")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.post(
            "/cpl/5",
            files=[("file", ("cpl.xlsx", BytesIO(b"\x00"), "application/octet-stream"))],
        )
        assert resp.status_code in (401, 403)

    def test_upload_failure(self, client, mock_db):
        """Service might raise 400 if CPL file format is invalid."""
        with patch("app.routes.pricelist._get_product_upload_payload", return_value={"status": "completed"}):
            with patch(
                "app.routes.pricelist.upload_cpl_service",
                side_effect=HTTPException(status_code=400, detail="Invalid CPL file format"),
            ) as mock_service:
                resp = client.post("/cpl/5", files=[self._xlsx_file()])
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower()
        mock_service.assert_called_once_with(
            db=mock_db,
            client_id=5,
            files=ANY,
            user_email=FAKE_ADMIN_USER["email"]
        )
