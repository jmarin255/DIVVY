from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import Expense, ExpenseSplit, Group, GroupMembership, User


def test_read_my_groups_returns_current_user_groups(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    group_owner = Group(name="Owner Group")
    group_member = Group(name="Member Group")
    group_other = Group(name="Other Group")
    other_user = User(
        first_name="Other",
        last_name="Person",
        email="other.person@example.com",
        password_hash=get_password_hash("password"),
    )

    db_session.add_all([group_owner, group_member, group_other, other_user])
    db_session.flush()

    db_session.add_all(
        [
            GroupMembership(
                user_id=authorized_user.id,
                group_id=group_owner.id,
                role="owner",
            ),
            GroupMembership(
                user_id=authorized_user.id,
                group_id=group_member.id,
                role="member",
            ),
            GroupMembership(
                user_id=other_user.id,
                group_id=group_other.id,
                role="owner",
            ),
        ]
    )
    db_session.commit()

    response = authorized_client.get("/api/v1/me/groups")

    assert response.status_code == 200
    body = response.json()
    returned_names = {group["name"] for group in body}
    assert returned_names == {"Owner Group", "Member Group"}

    roles_by_name = {group["name"]: group["role"] for group in body}
    assert roles_by_name["Owner Group"] == "owner"
    assert roles_by_name["Member Group"] == "member"


def test_read_my_expense_splits_returns_only_current_user_splits(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    group = Group(name="Trip")
    other_user = User(
        first_name="Split",
        last_name="Other",
        email="split.other@example.com",
        password_hash=get_password_hash("password"),
    )

    db_session.add_all([group, other_user])
    db_session.flush()

    db_session.add_all(
        [
            GroupMembership(user_id=authorized_user.id, group_id=group.id, role="owner"),
            GroupMembership(user_id=other_user.id, group_id=group.id, role="member"),
        ]
    )

    expense = Expense(
        group_id=group.id,
        created_by=authorized_user.id,
        name="Dinner",
        total_amount=100.0,
        description="Team dinner",
    )
    db_session.add(expense)
    db_session.flush()

    db_session.add_all(
        [
            ExpenseSplit(expense_id=expense.id, user_id=authorized_user.id, amount=40.0),
            ExpenseSplit(expense_id=expense.id, user_id=other_user.id, amount=60.0),
        ]
    )
    db_session.commit()

    response = authorized_client.get("/api/v1/me/expense-splits")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["user_id"] == authorized_user.id
    assert body[0]["expense_id"] == expense.id
    assert float(body[0]["amount"]) == 40.0


def test_read_my_owed_expenses_returns_expected_shape(
    authorized_client: TestClient,
    authorized_user: User,
    db_session: Session,
) -> None:
    group = Group(name="Household")
    db_session.add(group)
    db_session.flush()

    db_session.add(
        GroupMembership(user_id=authorized_user.id, group_id=group.id, role="owner")
    )

    expense = Expense(
        group_id=group.id,
        created_by=authorized_user.id,
        name="Utilities",
        total_amount=75.5,
        description="Monthly electric",
    )
    db_session.add(expense)
    db_session.flush()

    split = ExpenseSplit(
        expense_id=expense.id,
        user_id=authorized_user.id,
        amount=75.5,
    )
    db_session.add(split)
    db_session.commit()

    response = authorized_client.get("/api/v1/me/owed-expenses")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["expense_id"] == expense.id
    assert body[0]["split_id"] == split.id
    assert body[0]["group_id"] == group.id
    assert body[0]["name"] == "Utilities"
    assert float(body[0]["total_amount"]) == 75.5
    assert float(body[0]["amount_owed"]) == 75.5


def test_read_my_groups_returns_empty_list_when_no_memberships(
    authorized_client: TestClient,
) -> None:
    response = authorized_client.get("/api/v1/me/groups")

    assert response.status_code == 200
    assert response.json() == []
