from fastapi.testclient import TestClient
from sqlalchemy import select
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
    response = authorized_client.get("/api/v1/me/")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == authorized_user.id
    assert body["email"] == authorized_user.email
    assert body["first_name"] == authorized_user.first_name
    assert body["last_name"] == authorized_user.last_name


def test_read_user_by_id_returns_404_when_missing(
    authorized_client: TestClient,
) -> None:
    response = authorized_client.get("/api/v1/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_read_users_returns_all_users(
    authorized_client: TestClient,
    db_session: Session,
) -> None:
    user_1 = User(
        first_name="Alpha",
        last_name="One",
        email="alpha@example.com",
        password_hash=get_password_hash("password"),
    )
    user_2 = User(
        first_name="Beta",
        last_name="Two",
        email="beta@example.com",
        password_hash=get_password_hash("password"),
    )
    db_session.add_all([user_1, user_2])
    db_session.commit()

    response = authorized_client.get("/api/v1/users/")

    assert response.status_code == 200
    body = response.json()
    returned_emails = {user["email"] for user in body}
    assert "alpha@example.com" in returned_emails
    assert "beta@example.com" in returned_emails


def test_create_user_creates_new_user(client: TestClient, db_session: Session) -> None:
    payload = {
        "first_name": "New",
        "last_name": "User",
        "email": "new.user@example.com",
        "password": "password123",
        "phone": "+15551234567",
    }

    response = client.post("/api/v1/users/", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == payload["email"]
    assert body["first_name"] == payload["first_name"]
    assert body["last_name"] == payload["last_name"]

    created_user = db_session.execute(
        select(User).where(User.email == payload["email"])
    ).scalar_one_or_none()
    assert created_user is not None
    assert created_user.password_hash != payload["password"]


def test_create_user_returns_400_when_email_exists(
    client: TestClient,
    db_session: Session,
) -> None:
    existing_user = User(
        first_name="Existing",
        last_name="User",
        email="existing@example.com",
        password_hash=get_password_hash("password"),
    )
    db_session.add(existing_user)
    db_session.commit()

    payload = {
        "first_name": "Another",
        "last_name": "User",
        "email": "existing@example.com",
        "password": "password123",
    }

    response = client.post("/api/v1/users/", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_create_user_returns_400_when_phone_exists(
    client: TestClient,
    db_session: Session,
) -> None:
    existing_user = User(
        first_name="Existing",
        last_name="Phone",
        email="existing.phone@example.com",
        phone="+15557654321",
        password_hash=get_password_hash("password"),
    )
    db_session.add(existing_user)
    db_session.commit()

    payload = {
        "first_name": "Another",
        "last_name": "Phone",
        "email": "another.phone@example.com",
        "phone": "+15557654321",
        "password": "password123",
    }

    response = client.post("/api/v1/users/", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Phone number already registered"


def test_delete_user_deletes_self(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    response = authorized_client.delete(f"/api/v1/users/{authorized_user.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    deleted_user = db_session.execute(
        select(User).where(User.id == authorized_user.id)
    ).scalar_one_or_none()
    assert deleted_user is None


def test_delete_user_returns_403_when_not_self_and_not_dev(
    authorized_client: TestClient,
    db_session: Session,
) -> None:
    other_user = User(
        first_name="Other",
        last_name="User",
        email="other@example.com",
        password_hash=get_password_hash("password"),
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    response = authorized_client.delete(f"/api/v1/users/{other_user.id}")

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "You can only delete your own account unless you are a developer"
    )


def test_delete_user_returns_404_when_user_not_found_after_deletion(
    authorized_client: TestClient,
    authorized_user: User,
) -> None:
    first_response = authorized_client.delete(f"/api/v1/users/{authorized_user.id}")
    second_response = authorized_client.delete(f"/api/v1/users/{authorized_user.id}")

    assert first_response.status_code == 200
    assert second_response.status_code == 404
    assert second_response.json()["detail"] == "User not found"