import os
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID, uuid4

import aiofiles  # type: ignore
import pendulum
from fastapi import UploadFile
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import asc, desc, extract, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.settings.base import config_env, TZ
from src.config.settings.logger_config import logger
from src.models.db.category import Category, Category as CategoryModel
from src.models.db.expense import Expense as ExpenseModel
from src.models.db.user import User
from src.models.schemas.expense import Expense, ExpenseCreate, ExpenseUpdate, GeneralSummary, PagedExpense


async def create_expense(
    db: AsyncSession,
    user_id: UUID,
    expense: ExpenseCreate,
    invoice_image: Optional[UploadFile] = None,
) -> ExpenseModel:
    """
    Create a new expense asynchronously.

    Args:
        db (AsyncSession): The database session.
        user_id (UUID): The ID of the user creating the expense.
        expense (ExpenseCreate): The expense data to create.
        invoice_image (Optional[UploadFile]): The invoice image file, if any.

    Returns:
        ExpenseModel: The created expense model.

    Raises:
        RuntimeError: If there is an error creating the expense.
    """
    try:
        image_filename = None
        if invoice_image and invoice_image.filename:
            upload_dir = config_env.INVOICE_UPLOAD_DIR
            os.makedirs(upload_dir, exist_ok=True)

            file_extension = os.path.splitext(invoice_image.filename)[1]
            image_filename = f"{uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, image_filename)

            try:
                async with aiofiles.open(file_path, "wb") as out_file:
                    content = await invoice_image.read()
                    await out_file.write(content)
                logger.info(f"Invoice image saved successfully: {file_path}")
            except IOError as e:
                logger.error(f"Error saving invoice image: {e}")
                raise RuntimeError(f"Error saving invoice image: {e}") from e

        db_expense = ExpenseModel(
            subject=expense.subject,
            expense_date=expense.expense_date,
            reimbursable=expense.reimbursable,
            amount=expense.amount,
            description=expense.description,
            invoice_image=image_filename,
            employee=expense.employee,
            category_id=expense.category_id,
            user_id=user_id,
            updated_at=pendulum.now(tz=TZ).naive(),
        )
        db.add(db_expense)
        await db.commit()
        await db.refresh(db_expense)
        logger.info(f"Expense created successfully with subject: {expense.subject}")
        return db_expense
    except Exception as e:
        logger.error(f"Error creating expense: {e}")
        await db.rollback()
        raise RuntimeError(f"Error creating expense: {e}") from e


async def get_expense_by_id(db: AsyncSession, expense_id: UUID) -> ExpenseModel:
    """
    Retrieve an expense by ID asynchronously.

    Args:
        db (AsyncSession): The database session.
        expense_id (UUID): The ID of the expense to retrieve.

    Returns:
        ExpenseModel: The retrieved expense model.

    Raises:
        ValueError: If the expense is not found.
        RuntimeError: If there is an error retrieving the expense.
    """
    try:
        query = select(ExpenseModel).filter(ExpenseModel.expenses_id == expense_id)
        result = await db.execute(query)
        expense = result.scalars().first()
        if not expense:
            logger.warning(f"Expense not found with ID: {expense_id}")
            raise ValueError("Expense not found")
        logger.info(f"Expense retrieved successfully with ID: {expense_id}")
        return expense
    except ValueError as e:
        logger.error(f"Expense retrieval error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error retrieving expense with ID {expense_id}: {e}")
        raise RuntimeError("Error retrieving expense") from e


async def get_expenses(
    db: AsyncSession,
    params: Params,
    search: Optional[str] = None,
    sort_order: str = "desc",
) -> PagedExpense:
    """
    Retrieve expenses with pagination, filtering, and sorting asynchronously.
    Args:
        db (AsyncSession): The database session.
        params (Params): Pagination parameters.
        subject (Optional[str]): Filter by subject.
        expense_date (Optional[date]): Filter by expense date.
        reimbursable (Optional[bool]): Filter by reimbursable.
        employee (Optional[str]): Filter by employee name.
        sort_order (str): Sort order for expense_date, either 'asc' or 'desc'.
    Returns:
        PagedExpense: The list of filtered and sorted expense models.
    """
    try:
        query = select(ExpenseModel)
        if search:
            search = search.lower()
            query = query.filter(
                func.lower(ExpenseModel.subject).ilike(f"%{search}%")
                | func.lower(ExpenseModel.employee).ilike(f"%{search}%")
            )
        if sort_order == "asc":
            query = query.order_by(asc(ExpenseModel.expense_date))
        else:
            query = query.order_by(desc(ExpenseModel.expense_date))
        result = await paginate(db, query, params)
        logger.info(f"Total expenses retrieved: {len(result.items)}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving expenses: {e}")
        raise RuntimeError("Error retrieving expenses") from e


async def get_all_expenses(db: AsyncSession) -> List[Expense]:
    """
    Fetch all expense records asynchronously from the database.

    Args:
        db (AsyncSession): Database session.

    Returns:
        List[ExpenseSchema]: A list of all expense records.
    """
    try:
        logger.info("Executing query to fetch all expenses")
        result = await db.execute(select(ExpenseModel))
        expenses = result.scalars().all()

        expenses_schema = [Expense.from_orm(expense) for expense in expenses]

        logger.info(f"Total expenses retrieved: {len(expenses_schema)}")
        return expenses_schema
    except Exception as e:
        logger.error(f"Error while retrieving all expenses: {e}")
        raise RuntimeError("Error retrieving all expenses") from e


async def update_expense(
    db: AsyncSession,
    expense_id: UUID,
    expense_update: ExpenseUpdate,
    invoice_image: Optional[UploadFile] = None,
) -> ExpenseModel:
    """
    Update an expense by ID asynchronously.
    Args:
        db (AsyncSession): The database session.
        expense_id (UUID): The ID of the expense to update.
        expense_update (ExpenseUpdate): The expense data to update.
    Returns:
        ExpenseModel: The updated expense model.
    Raises:
        ValueError: If the expense is not found.
        RuntimeError: If there is an error updating the expense.
    """
    try:
        query = select(ExpenseModel).filter(ExpenseModel.expenses_id == expense_id)
        result = await db.execute(query)
        expense = result.scalars().first()
        if not expense:
            logger.warning(f"Expense not found with ID: {expense_id}")
            raise ValueError("Expense not found")
        if expense_update.category_id is not None:
            expense.category_id = expense_update.category_id
        if expense_update.subject is not None:
            expense.subject = expense_update.subject
        if expense_update.expense_date is not None:
            expense.expense_date = expense_update.expense_date
        if expense_update.amount is not None:
            expense.amount = expense_update.amount
        if expense_update.reimbursable is not None:
            expense.reimbursable = expense_update.reimbursable
        if expense_update.description is not None:
            expense.description = expense_update.description
        if expense_update.employee is not None:
            expense.employee = expense_update.employee
        if invoice_image and invoice_image.filename:
            if expense.invoice_image:
                old_file_path = os.path.join(config_env.INVOICE_UPLOAD_DIR, expense.invoice_image)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            file_extension = os.path.splitext(invoice_image.filename)[1]
            new_image_filename = f"{uuid4()}{file_extension}"
            new_file_path = os.path.join(config_env.INVOICE_UPLOAD_DIR, new_image_filename)
            async with aiofiles.open(new_file_path, "wb") as out_file:
                content = await invoice_image.read()
                await out_file.write(content)
            expense.invoice_image = new_image_filename
            logger.info(f"Invoice image updated successfully: {new_file_path}")
        expense.updated_at = pendulum.now(tz=TZ).naive()
        await db.commit()
        await db.refresh(expense)
        logger.info(f"Expense updated successfully with ID: {expense_id}")
        return expense
    except ValueError as e:
        logger.error(f"Expense update error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error updating expense with ID {expense_id}: {e}")
        raise RuntimeError("Error updating expense") from e


async def delete_expense(db: AsyncSession, expense_id: UUID) -> bool:
    """
    Delete an expense by ID asynchronously.

    Args:
        db (AsyncSession): The database session.
        expense_id (UUID): The ID of the expense to delete.

    Returns:
        bool: True if the expense was deleted successfully.

    Raises:
        ValueError: If the expense is not found.
        RuntimeError: If there is an error deleting the expense.
    """
    try:
        query = select(ExpenseModel).filter(ExpenseModel.expenses_id == expense_id)
        result = await db.execute(query)
        expense = result.scalars().first()
        if not expense:
            logger.warning(f"Expense not found with ID: {expense_id}")
            raise ValueError("Expense not found")

        if expense.invoice_image:
            old_file_path = os.path.join(config_env.INVOICE_UPLOAD_DIR, expense.invoice_image)
            try:
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    logger.info(f"Invoice image deleted with name: {expense.invoice_image}")
            except OSError as file_error:
                logger.error(f"Error deleting invoice image: {file_error}")
                raise RuntimeError("Error deleting invoice image") from file_error

        await db.delete(expense)
        await db.commit()
        logger.info(f"Expense deleted successfully with ID: {expense_id}")
        return True
    except ValueError as e:
        logger.error(f"Expense deletion error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error deleting expense with ID {expense_id}: {e}")
        await db.rollback()
        raise RuntimeError("Error deleting expense") from e


async def get_expenses_by_category(db: AsyncSession, year: int) -> list[dict]:
    """
    Retrieve expenses grouped by category for a specific year.
    Args:
        db (AsyncSession): The database session.
        year (int): The year for which to retrieve the expenses.
    Returns:
        list[dict]: A list of dictionaries containing category names and total expenses.
    """
    try:
        # Query to sum expenses by category for the specified year
        query = (
            select(Category.name, func.sum(ExpenseModel.amount).label("total_amount"))
            .join(Category, ExpenseModel.category_id == Category.category_id)
            .where(func.extract("year", ExpenseModel.expense_date) == year)
            .group_by(Category.name)
        )
        result = await db.execute(query)
        expenses_by_category = [{"category": row.name, "amount": float(row.total_amount)} for row in result]
        # Sort the results by amount in descending order
        expenses_by_category.sort(key=lambda x: x["amount"], reverse=True)
        return expenses_by_category
    except Exception as e:
        logger.error(f"Error retrieving expenses by category: {e}")
        raise RuntimeError("Error retrieving expenses by category") from e


async def get_last_5_months_summary(db: AsyncSession, year: int) -> list[dict]:
    """
    Retrieve the summary of expenses for the last 5 months of a given year.

    This function calculates the total expenses per month for the specified
    year and returns a summary containing the month names and corresponding
    total amounts. The last 5 months with recorded expenses are included
    in the result, sorted in descending order (most recent first).

    Args:
        db (AsyncSession): The database session for executing SQL queries.
        year (int): The year for which to retrieve the expense summary.

    Returns:
        list[dict]: A list of dictionaries where each dictionary contains
                    'month' (str) and 'amount' (float) keys representing
                    the month name and total expense amount respectively.
                    The list is sorted in descending order by month.

    Raises:
        RuntimeError: If there is an error retrieving the expense summary
                      from the database.
    """
    try:
        query = (
            select(ExpenseModel.expense_date, func.sum(ExpenseModel.amount).label("total_amount"))
            .where(func.extract("year", ExpenseModel.expense_date) == year)
            .group_by(ExpenseModel.expense_date)
            .order_by(ExpenseModel.expense_date)
        )

        result = await db.execute(query)
        raw_totals = result.all()

        logger.debug(f"Monthly totals (raw results): {raw_totals}")

        monthly_totals = {}

        for record in raw_totals:
            month = record.expense_date.strftime("%b")
            month_num = record.expense_date.month  # Get the month number

            if month not in monthly_totals:
                monthly_totals[month] = {"amount": 0.0, "month_num": month_num}
            monthly_totals[month]["amount"] += record.total_amount

            logger.debug(f"Processed record month: {month}, total_amount: {record.total_amount}")

        # Sort by month number in descending order and take the last 5
        sorted_months = sorted(monthly_totals.items(), key=lambda x: x[1]["month_num"], reverse=True)[:5]

        summary = [{"month": month, "amount": data["amount"]} for month, data in sorted_months]

        logger.info(f"Last 5 months summary retrieved for year {year}: {summary}")
        return summary

    except Exception as e:
        logger.error(f"Error retrieving last 5 months summary: {e}")
        raise RuntimeError("Error retrieving last 5 months summary") from e


async def get_recent_expenses(db: AsyncSession) -> list[dict]:
    """
    Retrieve the 5 most recent expenses.

    Args:
        db (AsyncSession): The database session.

    Returns:
        list[dict]: A list of dictionaries, each containing the expense details.
    """
    try:
        query = (
            select(
                ExpenseModel.subject,
                ExpenseModel.amount,
                User.username.label("added_by"),
                Category.name.label("category_name"),
            )
            .join(User, ExpenseModel.user_id == User.user_id)
            .join(Category, ExpenseModel.category_id == Category.category_id)
            .order_by(ExpenseModel.expense_date.desc())
            .limit(5)
        )
        result = await db.execute(query)
        raw_expenses = result.all()

        recent_expenses = [
            {
                "subject": expense.subject,
                "amount": expense.amount,
                "added_by": expense.added_by,
                "category_name": expense.category_name,
            }
            for expense in raw_expenses
        ]

        logger.info(f"Recent expenses retrieved: {recent_expenses}")
        return recent_expenses

    except Exception as e:
        logger.error(f"Error retrieving recent expenses: {e}")
        raise RuntimeError("Error retrieving recent expenses") from e


async def get_available_years(db: AsyncSession) -> list[int]:
    """
    Retrieve a list of distinct years from the expenses table.

    Args:
        db (AsyncSession): The database session.

    Returns:
        list[dict]: A list of dictionaries, each containing the expense details.
    """
    query = select(extract("year", ExpenseModel.expense_date).label("year")).distinct()
    result = await db.execute(query)
    years = [row.year for row in result]
    return sorted(years, reverse=True)


async def get_general_summary_data(db: AsyncSession, year: int) -> GeneralSummary:
    """
    Retrieve general summary of expenses for a specific user and year.

    Args:
        db (AsyncSession): The database session.
        year (int): The year for which to retrieve the summary.

    Returns:
        GeneralSummary: A summary of expense data.
    """
    # Base query for user's expenses filtered by the specified year
    base_query = select(func.sum(ExpenseModel.amount)).where(func.extract("year", ExpenseModel.expense_date) == year)

    # Query for total spending in the year
    total_spending_result = await db.execute(base_query)
    total_spending = float(total_spending_result.scalar() or 0)

    # Get the current year, month, and quarter
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_quarter = (current_month - 1) // 3 + 1

    # Determine last month and last quarter
    if current_month == 1:
        last_month = 12
        last_month_year = current_year - 1
    else:
        last_month = current_month - 1
        last_month_year = year

    last_quarter = current_quarter - 1
    if last_quarter == 0:
        last_quarter = 4
        last_quarter_year = current_year - 1
    else:
        last_quarter_year = current_year

    # Query for this month's spending
    this_month_spending_result = await db.execute(
        base_query.where(func.extract("month", ExpenseModel.expense_date) == current_month)
    )
    this_month_spending = float(this_month_spending_result.scalar() or 0)

    # Query for last month's spending
    last_month_spending_result = await db.execute(
        select(func.sum(ExpenseModel.amount)).where(
            func.extract("year", ExpenseModel.expense_date) == last_month_year,
            func.extract("month", ExpenseModel.expense_date) == last_month,
        )
    )
    last_month_spending = float(last_month_spending_result.scalar() or 0)

    # Query for this quarter's spending
    this_quarter_spending_result = await db.execute(
        base_query.where(
            func.extract("month", ExpenseModel.expense_date).in_(
                range((current_quarter - 1) * 3 + 1, current_quarter * 3 + 1)
            )
        )
    )
    this_quarter_spending = float(this_quarter_spending_result.scalar() or 0)

    # Query for last quarter's spending
    last_quarter_spending_result = await db.execute(
        select(func.sum(ExpenseModel.amount)).where(
            func.extract("year", ExpenseModel.expense_date) == last_quarter_year,
            func.extract("month", ExpenseModel.expense_date).in_(
                range((last_quarter - 1) * 3 + 1, last_quarter * 3 + 1)
            ),
        )
    )
    last_quarter_spending = float(last_quarter_spending_result.scalar() or 0)

    return GeneralSummary(
        total_spending=round(total_spending, 2),
        this_month=round(this_month_spending, 2),
        last_month=round(last_month_spending, 2),
        this_quarter=round(this_quarter_spending, 2),
        last_quarter=round(last_quarter_spending, 2),
    )
