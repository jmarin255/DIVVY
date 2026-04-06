from app.core.security import (
    require_dev,
)
from app.db.session import get_db
from app.models import (
    User,
)
from app.schemas.expense import ExpenseRead
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/expenses", tags=["expenses"])
from app.models import (
    Expense,
)


@router.get("/", response_model=list[ExpenseRead])
def read_expenses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_dev),
):
    """List groups for developer accounts only.

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
    groups = db.execute(statement).scalars().all()
    return groups
