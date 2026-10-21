"""Auth API contract: /api/auth/* (Better Auth, email + password)."""

import pytest
from playwright.sync_api import APIRequestContext

from conftest import register
from utils.test_data import new_member

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_sign_up_returns_session_token_and_user(api: APIRequestContext):
    m = new_member(name="API Member")

    body = register(api, m)

    assert body["token"], "a session token is issued on sign-up"
    assert body["user"]["email"] == m.email
    assert body["user"]["name"] == "API Member"


def test_session_token_identifies_the_member(api: APIRequestContext):
    m = new_member()
    token = register(api, m)["token"]

    response = api.get("/api/auth/get-session", headers={"Authorization": f"Bearer {token}"})

    assert response.status == 200
    assert response.json()["user"]["email"] == m.email


def test_anonymous_session_is_empty(api: APIRequestContext):
    response = api.get("/api/auth/get-session")

    assert response.status == 200
    assert response.json() is None


def test_duplicate_email_is_rejected(api: APIRequestContext):
    m = new_member()
    register(api, m)

    response = api.post(
        "/api/auth/sign-up/email", data={"email": m.email, "password": m.password, "name": m.name}
    )

    assert response.status == 422
    assert response.json()["code"] == "USER_ALREADY_EXISTS_USE_ANOTHER_EMAIL"


@pytest.mark.parametrize(
    ("email", "password", "expected_code"),
    [
        pytest.param("short.pw@example.test", "short", "PASSWORD_TOO_SHORT", id="password-under-8-chars"),
        pytest.param("not-an-email", "Test-pass-123", "VALIDATION_ERROR", id="malformed-email"),
    ],
)
def test_sign_up_input_validation(api: APIRequestContext, email, password, expected_code):
    response = api.post("/api/auth/sign-up/email", data={"email": email, "password": password, "name": "x"})

    assert response.status == 400
    assert response.json()["code"] == expected_code


def test_wrong_password_is_rejected(api: APIRequestContext):
    m = new_member()
    register(api, m)

    response = api.post("/api/auth/sign-in/email", data={"email": m.email, "password": "Wrong-pass-999"})

    assert response.status == 401
    assert response.json()["code"] == "INVALID_EMAIL_OR_PASSWORD"


def test_correct_password_signs_in(api: APIRequestContext):
    m = new_member()
    register(api, m)

    response = api.post("/api/auth/sign-in/email", data={"email": m.email, "password": m.password})

    assert response.status == 200
    assert response.json()["user"]["email"] == m.email
