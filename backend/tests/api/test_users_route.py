from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import User


def test_read_user_by_id_returns_user(
    authorized_client: TestClient,
    db_session: Session,
) -> None:
    test_user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password_hash=get_password_hash("password"),
    )

    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    response = authorized_client.get(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == test_user.id
    assert body["email"] == "test@example.com"
    assert body["first_name"] == "Test"
    assert body["last_name"] == "User"


def test_me(authorized_client: TestClient, authorized_user: User) -> None:
    response = authorized_client.get("/api/v1/users/me")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == authorized_user.id
    assert body["email"] == authorized_user.email
    assert body["first_name"] == authorized_user.first_name
    assert body["last_name"] == authorized_user.last_name