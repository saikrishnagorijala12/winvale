import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi import status
from tests.conftest import FAKE_ADMIN_USER
from datetime import datetime, timezone



NOW = datetime.now(timezone.utc).isoformat()


def _fake_job(**overrides):
    base = {
        "job_id": 1,
        "client_id": 1,
        "client_name": "Acme Corp",
        "status": "pending",
        "created_by": "admin@test.com",
        "created_time": NOW,
        "updated_time": NOW,
    }
    base.update(overrides)
    return base


def _fake_paginated_jobs(items=None, total=None):
    if items is None:
        items = [_fake_job()]
    if total is None:
        total = len(items)
    return {
        "total": total,
        "page": 1,
        "page_size": 50,
        "total_pages": 1,
        "items": items,
    }


class TestCreateJob:

    def test_success(self, client, mock_db):
        with patch("app.services.jobs.create_job", return_value=_fake_job(job_id=10)) as mock_service:
            resp = client.post("/jobs/1")
        assert resp.status_code == 200
        assert resp.json()["job_id"] == 10
        mock_service.assert_called_once_with(
            db=mock_db,
            client_id=1,
            user_email=FAKE_ADMIN_USER["email"]
        )

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.post("/jobs/1")
        assert resp.status_code in (401, 403)


class TestListJobs:

    def test_default_pagination(self, client, mock_db):
        with patch("app.services.jobs.list_jobs", return_value=_fake_paginated_jobs()) as mock_service:
            resp = client.get("/jobs")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search=None,
            client_id=None,
            status=None,
            date_from=None,
            date_to=None
        )

    def test_custom_pagination(self, client, mock_db):
        with patch("app.services.jobs.list_jobs", return_value=_fake_paginated_jobs()) as mock_service:
            resp = client.get("/jobs?page=2&page_size=10")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            page=2,
            page_size=10,
            search=None,
            client_id=None,
            status=None,
            date_from=None,
            date_to=None
        )

    def test_with_search_filter(self, client, mock_db):
        with patch("app.services.jobs.list_jobs", return_value=_fake_paginated_jobs()) as mock_service:
            resp = client.get("/jobs?search=acme")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search="acme",
            client_id=None,
            status=None,
            date_from=None,
            date_to=None
        )

    def test_with_client_id_filter(self, client, mock_db):
        with patch("app.services.jobs.list_jobs", return_value=_fake_paginated_jobs()) as mock_service:
            resp = client.get("/jobs?client_id=5")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search=None,
            client_id=5,
            status=None,
            date_from=None,
            date_to=None
        )

    def test_with_status_filter(self, client, mock_db):
        with patch("app.services.jobs.list_jobs", return_value=_fake_paginated_jobs()) as mock_service:
            resp = client.get("/jobs?status=pending")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search=None,
            client_id=None,
            status="pending",
            date_from=None,
            date_to=None
        )

    def test_with_date_range(self, client, mock_db):
        with patch("app.services.jobs.list_jobs", return_value=_fake_paginated_jobs()) as mock_service:
            resp = client.get(
                "/jobs?date_from=2025-01-01T00:00:00&date_to=2025-12-31T23:59:59"
            )
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search=None,
            client_id=None,
            status=None,
            date_from=ANY,
            date_to=ANY
        )

    def test_empty_results(self, client, mock_db):
        with patch(
            "app.services.jobs.list_jobs",
            return_value=_fake_paginated_jobs(items=[], total=0),
        ) as mock_service:
            resp = client.get("/jobs")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        mock_service.assert_called_once_with(
            db=mock_db,
            page=1,
            page_size=50,
            search=None,
            client_id=None,
            status=None,
            date_from=None,
            date_to=None
        )

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/jobs")
        assert resp.status_code in (401, 403)


class TestGetJobById:

    def test_success(self, client, mock_db):
        with patch("app.services.jobs.list_jobs_by_id", return_value=_fake_job(job_id=42)) as mock_service:
            resp = client.get("/jobs/42")
        assert resp.status_code == 200
        assert resp.json()["job_id"] == 42
        mock_service.assert_called_once_with(mock_db, 42, FAKE_ADMIN_USER["email"], 1, 50, None)

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/jobs/1")
        assert resp.status_code in (401, 403)



class TestUpdateJobStatus:

    def test_approve_success(self, client, mock_db):
        with patch("app.services.jobs.approve_job", return_value={"message": "approved"}) as mock_service:
            resp = client.post("/jobs/1/status?action=approve")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            job_id=1,
            user_email=FAKE_ADMIN_USER["email"]
        )

    def test_reject_success(self, client, mock_db):
        with patch("app.services.jobs.reject_job", return_value={"message": "rejected"}) as mock_service:
            resp = client.post("/jobs/1/status?action=reject")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            db=mock_db,
            job_id=1,
            user_email=FAKE_ADMIN_USER["email"]
        )

    def test_invalid_action(self, client):
        resp = client.post("/jobs/1/status?action=cancel")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_missing_action(self, client):
        resp = client.post("/jobs/1/status")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.post("/jobs/1/status?action=approve")
        assert resp.status_code in (401, 403)
