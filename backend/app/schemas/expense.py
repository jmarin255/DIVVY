from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExpenseBase(BaseModel):
    amount: float
    description: str | None = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseRead(ExpenseBase):
    id: int
    created_by: int
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class ExpenseSplit(BaseModel):
    user_id: int
    amount: float


class ExpenseSplitCreate(ExpenseSplit):
    pass


class ExpenseSplitRead(ExpenseSplit):
    id: int
    expense_id: int
    model_config = ConfigDict(from_attributes=True)


class ExpenseReadWithSplits(ExpenseRead):
    splits: list[ExpenseSplitRead] = []


class ExpenseOwedRead(BaseModel):
    expense_id: int
    split_id: int
    group_id: int
    created_by: int
    total_amount: float
    amount_owed: float
    description: str | None = None
    created_at: datetime | None = None
