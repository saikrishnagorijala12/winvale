import pytest
from unittest.mock import patch, MagicMock
from fastapi import status, HTTPException

from tests.conftest import FAKE_ADMIN_USER, FAKE_REGULAR_USER
import app.services.user as u


def _fake_user_dict(**overrides):
    """Return a realistic user response dict."""
    base = {
        "user_id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "phone_no": "9999999999",
        "is_active": True,
        "is_deleted": False,
        "role": "admin",
        "message": "Success",
    }
    base.update(overrides)
    return base



class TestGetMe:
    """GET /users/me — returns the current user via get_or_create_user dependency."""

    def test_success(self, client, mock_db):
        from main import app
        fake = _fake_user_dict(email=FAKE_ADMIN_USER["email"])

        def _override_get_or_create():
            return fake

        app.dependency_overrides[u.get_or_create_user] = _override_get_or_create
        resp = client.get("/users/me")
        assert resp.status_code == 200
        assert resp.json()["email"] == FAKE_ADMIN_USER["email"]
        del app.dependency_overrides[u.get_or_create_user]

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/users/me")
        assert resp.status_code in (401, 403)



class TestGetMyStatus:
    """GET /users/me/status — returns registration + active status."""

    def test_success(self, client, mock_db):
        with patch(
            "app.services.user.get_user_status_by_email",
            return_value={"registered": True, "is_active": True, "Role": "admin"},
        ) as mock_service:
            resp = client.get("/users/me/status")
        assert resp.status_code == 200
        assert resp.json()["registered"] is True
        mock_service.assert_called_once_with(mock_db, FAKE_ADMIN_USER["email"])

    def test_unregistered_user(self, client, mock_db):
        with patch(
            "app.services.user.get_user_status_by_email",
            return_value={"registered": False, "is_active": False},
        ) as mock_service:
            resp = client.get("/users/me/status")
        assert resp.status_code == 200
        assert resp.json()["registered"] is False
        mock_service.assert_called_once_with(mock_db, FAKE_ADMIN_USER["email"])

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/users/me/status")
        assert resp.status_code in (401, 403)


class TestGetCurrentUserByEmail:
    """GET /users — returns full profile of logged-in user."""

    def test_success(self, client, mock_db):
        fake = _fake_user_dict(email=FAKE_ADMIN_USER["email"])
        with patch("app.services.user.get_current_user_by_email", return_value=fake) as mock_service:
            resp = client.get("/users")
        assert resp.status_code == 200
        assert resp.json()["email"] == FAKE_ADMIN_USER["email"]
        mock_service.assert_called_once_with(mock_db, FAKE_ADMIN_USER["email"])

    def test_user_not_found_returns_error_dict(self, client, mock_db):
        with patch(
            "app.services.user.get_current_user_by_email",
            return_value={"Response Type": "Error", "Message": "User Not Found"},
        ) as mock_service:
            resp = client.get("/users")
        assert resp.status_code == 200
        assert resp.json()["Response Type"] == "Error"
        mock_service.assert_called_once_with(mock_db, FAKE_ADMIN_USER["email"])

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/users")
        assert resp.status_code in (401, 403)


VALID_USER_PAYLOAD = {
    "name": "New User",
    "email": "new@test.com",
    "phone_no": "8888888888",
    "cognito_sub": "sub-123",
    "role_name": "user",
}


class TestCreateUser:
    """POST /users — admin-only endpoint to create users."""

    def test_success(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.create_user_service",
                return_value=_fake_user_dict(user_id=10, email="new@test.com"),
            ) as mock_service:
                resp = client.post("/users", json=VALID_USER_PAYLOAD)
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["email"] == "new@test.com"
        mock_service.assert_called_once_with(
            mock_db,
            name="New User",
            email="new@test.com",
            phone_no="8888888888",
            role_name="user"
        )

    def test_conflict_duplicate_user(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.create_user_service",
                side_effect=u.UserAlreadyExistsError(),
            ) as mock_service:
                resp = client.post("/users", json=VALID_USER_PAYLOAD)
        assert resp.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in resp.json()["detail"].lower()
        mock_service.assert_called_once_with(
            mock_db,
            name="New User",
            email="new@test.com",
            phone_no="8888888888",
            role_name="user"
        )

    def test_validation_missing_name(self, client):
        bad = {**VALID_USER_PAYLOAD}
        bad.pop("name", None)
        resp = client.post("/users", json=bad)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_validation_invalid_email(self, client):
        bad = {**VALID_USER_PAYLOAD, "email": "not-an-email"}
        resp = client.post("/users", json=bad)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_validation_empty_body(self, client):
        resp = client.post("/users", json={})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.post("/users", json=VALID_USER_PAYLOAD)
        assert resp.status_code in (401, 403)

    def test_non_admin_forbidden(self, regular_client):
        with patch(
            "app.routes.users.require_admin",
            side_effect=HTTPException(status_code=403, detail="Admin only"),
        ):
            resp = regular_client.post("/users", json=VALID_USER_PAYLOAD)
        assert resp.status_code == 403



class TestUpdateUser:
    """PUT /users — logged-in user updates their own name/phone."""

    def test_success(self, client, mock_db):
        with patch(
            "app.services.user.update_user",
            return_value=_fake_user_dict(name="Updated Name"),
        ) as mock_service:
            resp = client.put("/users", json={"name": "Updated Name", "phone_no": "1111111111"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"
        mock_service.assert_called_once_with(
            mock_db,
            name="Updated Name",
            email=FAKE_ADMIN_USER["email"],
            phone_no="1111111111"
        )

    def test_partial_update_name_only(self, client, mock_db):
        with patch(
            "app.services.user.update_user",
            return_value=_fake_user_dict(name="Only Name"),
        ) as mock_service:
            resp = client.put("/users", json={"name": "Only Name"})
        assert resp.status_code == 200
        mock_service.assert_called_once_with(
            mock_db,
            name="Only Name",
            email=FAKE_ADMIN_USER["email"],
            phone_no=None
        )

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.put("/users", json={"name": "X"})
        assert resp.status_code in (401, 403)




class TestApproveRejectUser:
    """PATCH /users/{id}/approve — admin approves or rejects a user."""

    def test_approve_success(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch("app.services.user.approve_user_service", return_value=True) as mock_service:
                resp = client.patch("/users/5/approve?action=approve")
        assert resp.status_code == 200
        assert resp.json()["message"] == "User approved"
        mock_service.assert_called_once_with(mock_db, user_id=5)

    def test_reject_success(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch("app.services.user.reject_user_service", return_value=True) as mock_service:
                resp = client.patch("/users/5/approve?action=reject")
        assert resp.status_code == 200
        assert resp.json()["message"] == "User rejected"
        mock_service.assert_called_once_with(mock_db, user_id=5)

    def test_user_not_found(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.approve_user_service",
                side_effect=u.UserNotFoundError(),
            ) as mock_service:
                resp = client.patch("/users/999/approve?action=approve")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        mock_service.assert_called_once_with(mock_db, user_id=999)

    def test_invalid_action_rejected(self, client):
        """Query param must match ^(approve|reject)$"""
        resp = client.patch("/users/5/approve?action=suspend")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_missing_action_param(self, client):
        resp = client.patch("/users/5/approve")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_non_admin_forbidden(self, regular_client):
        with patch(
            "app.routes.users.require_admin",
            side_effect=HTTPException(status_code=403, detail="Admin only"),
        ):
            resp = regular_client.patch("/users/5/approve?action=approve")
        assert resp.status_code == 403



class TestGetAllUsers:
    """GET /users/all — admin-only listing."""

    def test_success(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.get_all_users",
                return_value={
                    "users": [_fake_user_dict()],
                    "total_count": 1,
                    "status_counts": {"all": 1, "pending": 0, "approved": 1, "rejected": 0},
                },
            ) as mock_service:
                resp = client.get("/users/all")
        assert resp.status_code == 200
        data = resp.json()
        assert "users" in data
        assert len(data["users"]) == 1
        mock_service.assert_called_once_with(
            db=mock_db, skip=0, limit=10, status="all", search=None
        )

    def test_empty_list(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.get_all_users",
                return_value={
                    "users": [],
                    "total_count": 0,
                    "status_counts": {"all": 0, "pending": 0, "approved": 0, "rejected": 0},
                },
            ) as mock_service:
                resp = client.get("/users/all")
        assert resp.status_code == 200
        assert resp.json()["users"] == []
        mock_service.assert_called_once_with(
            db=mock_db, skip=0, limit=10, status="all", search=None
        )

    def test_filter_pending(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.get_all_users",
                return_value={
                    "users": [],
                    "total_count": 0,
                    "status_counts": {"all": 10, "pending": 0, "approved": 10, "rejected": 0},
                },
            ) as mock_service:
                resp = client.get("/users/all?status=pending")
        assert resp.status_code == 200
        assert resp.json()["users"] == []
        mock_service.assert_called_once_with(
            db=mock_db, skip=0, limit=10, status="pending", search=None
        )

    def test_non_admin_forbidden(self, regular_client):
        """require_admin returns False → route raises 403."""
        with patch("app.routes.users.require_admin", return_value=False):
            resp = regular_client.get("/users/all")
        assert resp.status_code == 403

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.get("/users/all")
        assert resp.status_code in (401, 403)



class TestDeleteUser:
    """DELETE /users/{id} — admin soft-deletes a user."""

    def test_success(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.delete_user",
                return_value=_fake_user_dict(is_deleted=True, is_active=False),
            ) as mock_service:
                resp = client.delete("/users/5")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(mock_db, 5)

    def test_user_not_found(self, client, mock_db):
        """UserNotFoundError is raised and caught in the route -> 404."""
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.delete_user",
                side_effect=u.UserNotFoundError(),
            ) as mock_service:
                resp = client.delete("/users/999")
        assert resp.status_code == 404
        mock_service.assert_called_once_with(mock_db, 999)

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.delete("/users/5")
        assert resp.status_code in (401, 403)



class TestChangeRole:
    """PUT /users/change_role/{id} — admin toggles user role."""

    def test_success(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.change_user_role",
                return_value=_fake_user_dict(role="user"),
            ) as mock_service:
                resp = client.put("/users/change_role/5")
        assert resp.status_code == 200
        mock_service.assert_called_once_with(mock_db, 5, FAKE_ADMIN_USER["email"])

    def test_self_change_forbidden(self, client, mock_db):
        with patch("app.routes.users.require_admin", return_value=True):
            with patch(
                "app.services.user.change_user_role",
                side_effect=HTTPException(status_code=403, detail="Action Not Allowed"),
            ) as mock_service:
                resp = client.put("/users/change_role/1")
        assert resp.status_code == 403
        mock_service.assert_called_once_with(mock_db, 1, FAKE_ADMIN_USER["email"])

    def test_unauthenticated(self, unauth_client):
        resp = unauth_client.put("/users/change_role/5")
        assert resp.status_code in (401, 403)


class TestBulkApproveUsers:

    def test_success(self, client, mock_db):
        payload = {"user_ids": [10, 11], "action": "approve"}
        with patch("app.routes.users.require_admin", return_value=True):
            with patch("app.services.user.bulk_update_user_status") as mock_service:
                # Assuming the service returns some data or just succeeds
                mock_service.return_value = [{"user_id": 10, "status": "approved"}, {"user_id": 11, "status": "approved"}]
                resp = client.patch("/users/bulk-approve", json=payload)
        
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        assert len(data["results"]) == 2
        mock_service.assert_called_once_with(db=mock_db, user_ids=[10, 11], action="approve")

    def test_non_admin_forbidden(self, regular_client):
        payload = {"user_ids": [10, 11], "action": "approve"}
        with patch("app.routes.users.require_admin", side_effect=HTTPException(status_code=403)):
            resp = regular_client.patch("/users/bulk-approve", json=payload)
        assert resp.status_code == 403
