from app.core.security import get_current_user
from app.db.session import get_db
from app.models import (
    Expense as ExpenseModel,
    ExpenseSplit as ExpenseSplitModel,
    GroupMembership,
    User,
)
from app.schemas.expense import ExpenseOwedRead, ExpenseSplitRead
from app.schemas.group import GroupWithMembership
from app.schemas.user import UserRead
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/", response_model=UserRead)
def read_my_profile(current_user: User = Depends(get_current_user)):
    """Return profile for the currently authenticated user.

    Validation:
    - Access token must map to an existing user.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    return current_user


@router.get("/groups", response_model=list[GroupWithMembership])
def read_my_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return groups where the current user has membership.

    Validation:
    - Access token must map to an existing user.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    memberships = (
        db.execute(
            select(GroupMembership).where(
                GroupMembership.user_id == int(getattr(current_user, "id"))
            )
        )
        .scalars()
        .all()
    )

    return [
        GroupWithMembership(
            id=int(getattr(membership.group, "id")),
            name=str(getattr(membership.group, "name")),
            join_code=str(getattr(membership.group, "join_code")),
            created_at=getattr(membership.group, "created_at"),
            role=str(getattr(membership, "role")),
            joined_at=getattr(membership, "joined_at"),
        )
        for membership in memberships
    ]


@router.get("/expense-splits", response_model=list[ExpenseSplitRead])
def read_my_expense_splits(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return expense splits assigned to the currently authenticated user.

    Validation:
    - Access token must map to an existing user.
    - `skip` and `limit` query params are optional pagination controls.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    splits = (
        db.execute(
            select(ExpenseSplitModel)
            .where(ExpenseSplitModel.user_id == int(getattr(current_user, "id")))
            .order_by(ExpenseSplitModel.id.desc())
            .offset(skip)
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return splits


@router.get("/owed-expenses", response_model=list[ExpenseOwedRead])
def read_my_owed_expenses(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return detailed expenses where the current user owes a split amount.

    Validation:
    - Access token must map to an existing user.
    - `skip` and `limit` query params are optional pagination controls.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    current_user_id = int(getattr(current_user, "id"))

    rows = db.execute(
        select(ExpenseSplitModel, ExpenseModel)
        .join(ExpenseModel, ExpenseModel.id == ExpenseSplitModel.expense_id)
        .where(ExpenseSplitModel.user_id == current_user_id)
        .order_by(ExpenseModel.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()

    return [
        ExpenseOwedRead(
            expense_id=int(getattr(expense, "id")),
            split_id=int(getattr(split, "id")),
            group_id=int(getattr(expense, "group_id")),
            created_by=int(getattr(expense, "created_by")),
            total_amount=float(getattr(expense, "total_amount")),
            amount_owed=float(getattr(split, "amount")),
            description=getattr(expense, "description"),
            created_at=getattr(expense, "created_at"),
        )
        for split, expense in rows
    ]

