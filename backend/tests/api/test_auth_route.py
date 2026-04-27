from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models import RefreshSession, User


def test_login_returns_access_token_and_sets_refresh_cookie(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(
        first_name="Auth",
        last_name="User",
        email="auth.user@example.com",
        password_hash=get_password_hash("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["id"] == user.id

    refresh_cookie_name = settings.REFRESH_TOKEN_COOKIE_NAME
    assert refresh_cookie_name in response.cookies
    assert response.cookies.get(refresh_cookie_name)

    refresh_session = db_session.execute(
        select(RefreshSession).where(
            RefreshSession.user_id == user.id,
            RefreshSession.revoked_at.is_(None),
        )
    ).scalar_one_or_none()
    assert refresh_session is not None


def test_login_returns_401_for_invalid_credentials(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(
        first_name="Invalid",
        last_name="Login",
        email="invalid.login@example.com",
        password_hash=get_password_hash("correct-password"),
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_refresh_rotates_refresh_session(
    client: TestClient,
    db_session: Session,
) -> None:
    user = User(
        first_name="Rotate",
        last_name="Session",
        email="rotate.session@example.com",
        password_hash=get_password_hash("password123"),
    )
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "password123"},
    )
    assert login_response.status_code == 200

    refresh_response = client.post("/api/v1/auth/refresh")

    assert refresh_response.status_code == 200
    body = refresh_response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"

    sessions = db_session.execute(
        select(RefreshSession).where(RefreshSession.user_id == user.id)
    ).scalars().all()
    assert len(sessions) == 2
    revoked_count = sum(1 for session in sessions if session.revoked_at is not None)
    active_count = sum(1 for session in sessions if session.revoked_at is None)
    assert revoked_count == 1
    assert active_count == 1


def test_refresh_returns_401_without_cookie(client: TestClient) -> None:
    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token is missing"


def test_logout_returns_400_without_cookie(client: TestClient) -> None:
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 400
    assert response.json()["detail"] == "Refresh token cookie is missing"
