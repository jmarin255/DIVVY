from app.core.security import (
    get_current_user,
    is_dev_user,
    require_dev,
)
from app.db.session import get_db
from app.models import (
    Expense,
    ExpenseSplit,
    Group,
    GroupMembership,
    User,
)
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseSplitCreate, ExpenseSplitRead
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/expenses", tags=["expenses"])


def _is_group_member(db: Session, group_id: int, user_id: int) -> bool:
    membership = db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == user_id,
        )
    ).scalar_one_or_none()
    return membership is not None


def _is_group_owner(db: Session, group_id: int, user_id: int) -> bool:
    membership = db.execute(
        select(GroupMembership).where(
            GroupMembership.group_id == group_id,
            GroupMembership.user_id == user_id,
            GroupMembership.role == "owner",
        )
    ).scalar_one_or_none()
    return membership is not None


def _ensure_can_access_group(
    db: Session,
    group_id: int,
    current_user: User,
) -> None:
    group = db.execute(select(Group).where(Group.id == group_id)).scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")

    current_user_id = int(getattr(current_user, "id"))
    if is_dev_user(current_user) or _is_group_member(db, group_id, current_user_id):
        return

    raise HTTPException(
        status_code=403,
        detail="Only group members or developers can access this group's expenses",
    )


def _to_expense_read(expense: Expense) -> ExpenseRead:
    return ExpenseRead(
        id=int(getattr(expense, "id")),
        name=str(getattr(expense, "name")),
        amount=float(getattr(expense, "total_amount")),
        description=getattr(expense, "description"),
        created_by=int(getattr(expense, "created_by")),
        created_at=getattr(expense, "created_at"),
    )


@router.get("/", response_model=list[ExpenseRead])
def read_expenses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_dev),
):
    """List expenses for developer accounts only.

    Validation:
    - `skip` and `limit` query params are optional pagination controls.
    - Caller must be a developer email from `DEV_EMAILS`.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    statement = (
        select(Expense).order_by(Expense.created_at.desc()).offset(skip).limit(limit)
    )
    expenses = db.execute(statement).scalars().all()
    return [_to_expense_read(expense) for expense in expenses]


@router.get("/{expense_id}", response_model=ExpenseRead)
def read_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single expense by id when caller can access its group.

    Validation:
    - `expense_id` must exist or returns 404.
    - Caller must be a member of the related group or a developer.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    expense = db.execute(
        select(Expense).where(Expense.id == expense_id)
    ).scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    _ensure_can_access_group(db, int(getattr(expense, "group_id")), current_user)
    return _to_expense_read(expense)


@router.get("/group/{group_id}", response_model=list[ExpenseRead])
def read_group_expenses(
    group_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List expenses for a group the caller can access.

    Validation:
    - `group_id` must exist or returns 404.
    - Caller must be a member of `group_id` or a developer.
    - `skip` and `limit` query params are optional pagination controls.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    _ensure_can_access_group(db, group_id, current_user)

    expenses = (
        db.execute(
            select(Expense)
            .where(Expense.group_id == group_id)
            .order_by(Expense.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return [_to_expense_read(expense) for expense in expenses]


@router.post("/group/{group_id}", response_model=ExpenseRead)
def create_expense(
    group_id: int,
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new expense in a group the caller can access.

    Validation:
    - `group_id` must exist or returns 404.
    - Caller must be a member of `group_id` or a developer.
    - Request body must match `ExpenseCreate`.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    _ensure_can_access_group(db, group_id, current_user)

    new_expense = Expense(
        group_id=group_id,
        created_by=int(getattr(current_user, "id")),
        name=expense.name,
        total_amount=expense.amount,
        description=expense.description,
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return _to_expense_read(new_expense)


@router.post("/{expense_id}/splits", response_model=list[ExpenseSplitRead])
def create_expense_splits(
    expense_id: int,
    splits: list[ExpenseSplitCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create splits for an existing expense.

    Validation:
    - `expense_id` must exist or returns 404.
    - Caller must be in the expense's group or be a developer.
    - Caller must be expense creator, group owner, or developer.
    - Request body must be a non-empty list of `ExpenseSplitCreate`.
    - Each split user must be a member of the expense's group.
    - Total split amount must match the expense total amount.
    - Expense cannot already have splits.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    expense = db.execute(
        select(Expense).where(Expense.id == expense_id)
    ).scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    if not splits:
        raise HTTPException(status_code=400, detail="At least one split is required")

    expense_group_id = int(getattr(expense, "group_id"))
    _ensure_can_access_group(db, expense_group_id, current_user)

    current_user_id = int(getattr(current_user, "id"))
    if (
        not is_dev_user(current_user)
        and int(getattr(expense, "created_by")) != current_user_id
        and not _is_group_owner(db, expense_group_id, current_user_id)
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the creator, group owner, or a developer can add splits to this expense",
        )

    existing_split = db.execute(
        select(ExpenseSplit).where(ExpenseSplit.expense_id == expense_id)
    ).scalar_one_or_none()
    if existing_split is not None:
        raise HTTPException(
            status_code=400,
            detail="Splits already exist for this expense",
        )

    split_user_ids = [split.user_id for split in splits]
    if len(split_user_ids) != len(set(split_user_ids)):
        raise HTTPException(
            status_code=400,
            detail="Each user can only have one split per expense",
        )

    for split in splits:
        if not _is_group_member(db, expense_group_id, split.user_id):
            raise HTTPException(
                status_code=400,
                detail=f"User {split.user_id} is not a member of this group",
            )

    expense_total = float(getattr(expense, "total_amount"))
    split_total = sum(float(split.amount) for split in splits)
    if abs(split_total - expense_total) > 0.01:
        raise HTTPException(
            status_code=400,
            detail="Split amounts must add up to the total expense amount",
        )

    created_splits: list[ExpenseSplit] = []
    for split in splits:
        db_split = ExpenseSplit(
            expense_id=expense_id,
            user_id=split.user_id,
            amount=split.amount,
        )
        db.add(db_split)
        created_splits.append(db_split)

    db.commit()
    for db_split in created_splits:
        db.refresh(db_split)

    return created_splits


@router.put("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an expense when caller has write permission.

    Validation:
    - `expense_id` must exist or returns 404.
    - Caller must be in the expense's group or be a developer.
    - Caller must be expense creator, group owner, or developer.
    - Request body must match `ExpenseCreate`.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    expense = db.execute(
        select(Expense).where(Expense.id == expense_id)
    ).scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense_group_id = int(getattr(expense, "group_id"))
    _ensure_can_access_group(db, expense_group_id, current_user)

    current_user_id = int(getattr(current_user, "id"))
    if (
        not is_dev_user(current_user)
        and int(getattr(expense, "created_by")) != current_user_id
        and not _is_group_owner(db, expense_group_id, current_user_id)
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the creator, group owner, or a developer can update this expense",
        )

    setattr(expense, "total_amount", expense_in.amount)
    setattr(expense, "name", expense_in.name)
    setattr(expense, "description", expense_in.description)
    db.commit()
    db.refresh(expense)
    return _to_expense_read(expense)


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an expense when caller has write permission.

    Validation:
    - `expense_id` must exist or returns 404.
    - Caller must be in the expense's group or be a developer.
    - Caller must be expense creator, group owner, or developer.

    Auth input:
    - Requires bearer access token in `Authorization` header.
    - No refresh cookie required.
    - No token in request body.
    """
    expense = db.execute(
        select(Expense).where(Expense.id == expense_id)
    ).scalar_one_or_none()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense_group_id = int(getattr(expense, "group_id"))
    _ensure_can_access_group(db, expense_group_id, current_user)

    current_user_id = int(getattr(current_user, "id"))
    if (
        not is_dev_user(current_user)
        and int(getattr(expense, "created_by")) != current_user_id
        and not _is_group_owner(db, expense_group_id, current_user_id)
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the creator, group owner, or a developer can delete this expense",
        )

    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}
