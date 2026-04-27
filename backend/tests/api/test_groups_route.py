from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import Group, GroupMembership, User


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


def test_read_group_by_id_returns_404_when_group_missing(client: TestClient) -> None:
    response = client.get("/api/v1/groups/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_create_group_creates_owner_membership(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    response = authorized_client.post("/api/v1/groups/", json={"name": "Beach Trip"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Beach Trip"
    assert len(body["join_code"]) == 5

    owner_membership = db_session.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == body["id"],
            GroupMembership.user_id == authorized_user.id,
            GroupMembership.role == "owner",
        )
    ).scalar_one_or_none()
    assert owner_membership is not None


def test_join_group_by_code_adds_membership(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    group = Group(name="Roommates")
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    response = authorized_client.post(f"/api/v1/groups/join/{group.join_code}")

    assert response.status_code == 200
    membership = db_session.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group.id,
            GroupMembership.user_id == authorized_user.id,
        )
    ).scalar_one_or_none()
    assert membership is not None
    assert membership.role == "member"


def test_join_group_by_code_returns_400_when_already_member(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    group = Group(name="Existing Group")
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    existing_membership = GroupMembership(
        user_id=authorized_user.id,
        group_id=group.id,
        role="member",
    )
    db_session.add(existing_membership)
    db_session.commit()

    response = authorized_client.post(f"/api/v1/groups/join/{group.join_code}")

    assert response.status_code == 400
    assert response.json()["detail"] == "User is already a member of the group"


def test_delete_group_deletes_when_requester_is_owner(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    group = Group(name="Delete Group")
    db_session.add(group)
    db_session.flush()
    db_session.add(
        GroupMembership(user_id=authorized_user.id, group_id=group.id, role="owner")
    )
    db_session.commit()

    response = authorized_client.delete(f"/api/v1/groups/{group.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Group deleted successfully"

    deleted_group = db_session.execute(
        select(Group).where(Group.id == group.id)
    ).scalar_one_or_none()
    assert deleted_group is None


def test_add_user_to_group_adds_member_when_requester_is_owner(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    target_user = User(
        first_name="Target",
        last_name="User",
        email="target@example.com",
        password_hash=get_password_hash("password"),
    )
    group = Group(name="Add User Group")
    db_session.add_all([target_user, group])
    db_session.flush()
    db_session.add(
        GroupMembership(user_id=authorized_user.id, group_id=group.id, role="owner")
    )
    db_session.commit()

    response = authorized_client.post(f"/api/v1/groups/{group.id}/users/{target_user.id}")

    assert response.status_code == 200
    membership = db_session.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group.id,
            GroupMembership.user_id == target_user.id,
        )
    ).scalar_one_or_none()
    assert membership is not None
    assert membership.role == "member"


def test_add_user_to_group_returns_403_for_non_owner_non_dev(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    owner_user = User(
        first_name="Owner",
        last_name="User",
        email="owner@example.com",
        password_hash=get_password_hash("password"),
    )
    target_user = User(
        first_name="Target",
        last_name="User",
        email="another.target@example.com",
        password_hash=get_password_hash("password"),
    )
    group = Group(name="Permission Group")
    db_session.add_all([owner_user, target_user, group])
    db_session.flush()
    db_session.add(GroupMembership(user_id=owner_user.id, group_id=group.id, role="owner"))
    db_session.add(GroupMembership(user_id=authorized_user.id, group_id=group.id, role="member"))
    db_session.commit()

    response = authorized_client.post(f"/api/v1/groups/{group.id}/users/{target_user.id}")

    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "You can only manage yourself unless you are the group owner or a developer"
    )


def test_remove_user_from_group_removes_membership_when_requester_is_owner(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    target_user = User(
        first_name="Remove",
        last_name="Me",
        email="remove@example.com",
        password_hash=get_password_hash("password"),
    )
    group = Group(name="Remove User Group")
    db_session.add_all([target_user, group])
    db_session.flush()

    owner_membership = GroupMembership(
        user_id=authorized_user.id,
        group_id=group.id,
        role="owner",
    )
    target_membership = GroupMembership(
        user_id=target_user.id,
        group_id=group.id,
        role="member",
    )
    db_session.add_all([owner_membership, target_membership])
    db_session.commit()

    response = authorized_client.delete(f"/api/v1/groups/{group.id}/users/{target_user.id}")

    assert response.status_code == 200
    membership = db_session.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group.id,
            GroupMembership.user_id == target_user.id,
        )
    ).scalar_one_or_none()
    assert membership is None
