import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from fastapi_pagination import Page
from pydantic import BaseModel, ConfigDict, Field, validator


class ExpenseBase(BaseModel):
    """
    Schema representing the base fields for creating and updating an expense.
    """

    category_id: UUID
    subject: str = Field(..., min_length=2, max_length=100)
    expense_date: date
    amount: float = Field(..., gt=0)
    reimbursable: bool = Field(default=False)
    invoice_image: Optional[str]
    description: Optional[str] = Field(default=None, max_length=500)
    employee: Optional[str] = Field(default=None, max_length=100)

    @validator("description")
    def description_must_have_two_words(cls, description):
        if description is not None and len(description.split()) < 2:
            raise ValueError("Description must contain at least two words")
        return description

    @validator("employee")
    def employee_name_validation(cls, employee):
        if employee is not None:
            if len(employee) < 2:
                raise ValueError("Employee name must contain at least two characters")
            if re.match(r"^\d", employee):
                raise ValueError("Employee name cannot start with a number")
        return employee


class ExpenseCreate(BaseModel):
    """
    Schema representing the fields required to create a new expense.
    Inherits: ExpenseBase: Base schema with common expense fields.
    """

    category_id: UUID
    subject: str = Field(..., min_length=2, max_length=100)
    expense_date: date
    amount: float = Field(..., gt=0)
    reimbursable: bool = Field(default=False)
    description: Optional[str] = Field(default=None, max_length=500)
    employee: Optional[str] = Field(default=None, max_length=100)

    @validator("description")
    def description_must_have_two_words(cls, description):
        if description is not None and len(description.split()) < 2:
            raise ValueError("Description must contain at least two words")
        return description

    @validator("employee")
    def employee_name_validation(cls, employee):
        if employee is not None:
            if len(employee) < 2:
                raise ValueError("Employee name must contain at least two characters")
            if re.match(r"^\d", employee):
                raise ValueError("Employee name cannot start with a number")
        return employee


class ExpenseUpdate(ExpenseCreate):
    """
    Schema representing the fields required to update an expense.
    All fields are optional to allow partial updates.
    """


class GeneralSummary(BaseModel):
    """
    Schema representing a summary of general spending information.

    Attributes:
        total_spending (float): The total amount spent across all expenses.
        this_month (float): The total amount spent in the current month.
        last_month (float): The total amount spent in the previous month.
        this_quarter (float): The total amount spent in the current quarter.
        last_quarter (float): The total amount spent in the previous quarter.
    """

    total_spending: float
    this_month: float
    last_month: float
    this_quarter: float
    last_quarter: float


class Expense(ExpenseBase):
    """
    Schema representing an expense with a unique identifier.
    """

    expenses_id: UUID
    user_id: UUID
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        },
    )


PagedExpense = Page[Expense]
