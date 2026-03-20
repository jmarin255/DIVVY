from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Group


def test_read_group_by_id_returns_group(client: TestClient, db_session: Session) -> None:
    test_group = Group(name="Test Group")
    db_session.add(test_group)
    db_session.commit()
    db_session.refresh(test_group)

    response = client.get(f"/api/v1/groups/{test_group.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == test_group.id
    assert body["name"] == "Test Group"
