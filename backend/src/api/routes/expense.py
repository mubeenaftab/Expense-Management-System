import json
from datetime import date
from typing import List, Optional
from uuid import UUID

import pendulum
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, status, UploadFile
from fastapi_pagination import add_pagination, Params
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings.logger_config import logger
from src.models.schemas.error_response import ErrorResponse
from src.models.schemas.expense import (
    Expense as ExpenseSchema,
    ExpenseCreate,
    ExpenseUpdate,
    GeneralSummary,
    PagedExpense,
)
from src.models.schemas.user import User
from src.repository.crud.expense import (
    create_expense,
    delete_expense,
    get_all_expenses,
    get_available_years,
    get_expense_by_id,
    get_expenses,
    get_expenses_by_category,
    get_general_summary_data,
    get_last_5_months_summary,
    get_recent_expenses,
    update_expense,
)
from src.repository.database import get_db
from src.securities.verification.credentials import get_current_user
from src.utilities.messages.exceptions.http.exc_details import (
    available_years_unexpected_error,
    expense_deletion_not_found,
    expense_invalid_year_format,
    expense_not_found,
    expense_recent_not_found,
    expense_summary_not_found_for_year,
    expense_unexpected_error_create,
    expense_unexpected_error_delete,
    expense_unexpected_error_list,
    expense_unexpected_error_retrieve_by_id,
    expense_unexpected_error_retrieve_recent,
    expense_unexpected_error_retrieve_summary_by_year,
    expense_unexpected_error_update,
    expense_update_not_found,
    expenses_by_category_unexpected_error,
    expenses_not_found,
    general_summary_unexpected_error,
)

router = APIRouter()


@router.get(
    "/expenses/available-years",
    response_model=list[int],
    status_code=status.HTTP_200_OK,
)
async def get_available_years_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[int]:
    """
    Endpoint to retrieve available years for expenses.

    Returns:
        list[int]: A list of distinct years.
    """
    try:
        return await get_available_years(db)
    except Exception as e:
        logger.error(f"Unexpected error while retrieving available years: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=available_years_unexpected_error(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.post(
    "/expenses",
    response_model=ExpenseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def create_expense_endpoint(
    expense: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    invoice_image: Optional[UploadFile] = File(None),
) -> ExpenseSchema:
    """
    Create a new expense.

    Args:
        expense (str): The expense data to create, as a JSON string.
        current_user (User): The current authenticated user.
        db (AsyncSession): The database session.
        invoice_image (UploadFile, optional): The invoice image file.

    Returns:
        ExpenseSchema: The created expense object.
    """
    try:
        expense_data = json.loads(expense)
        expense_obj = ExpenseCreate(**expense_data)

        db_expense = await create_expense(db, current_user.user_id, expense_obj, invoice_image)
        logger.info(f"Expense created successfully with ID: {db_expense.expenses_id}")
        return ExpenseSchema.model_validate(db_expense)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in expense data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                detail="Invalid JSON in expense data",
                status_code=status.HTTP_400_BAD_REQUEST,
            ).model_dump(),
        ) from e
    except ValueError as e:
        logger.error(f"Error creating expense: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                detail=str(e),
                status_code=status.HTTP_400_BAD_REQUEST,
            ).model_dump(),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error during expense creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=expense_unexpected_error_create(expense_obj.subject),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).model_dump(),
        ) from e


@router.get(
    "/expenses/recent",
    response_model=list[dict],
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_recent_expenses_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """
    Retrieve the 5 most recent expenses.

    Args:
        db (AsyncSession): The database session.
        current_user (User): The currently logged-in user.

    Returns:
        list[dict]: A list of the 5 most recent expenses.
    """
    try:
        logger.info("Fetching the 5 most recent expenses")
        recent_expenses = await get_recent_expenses(db)

        if not recent_expenses:
            logger.warning("No recent expenses found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    detail=expense_recent_not_found(),
                    status_code=status.HTTP_404_NOT_FOUND,
                ).dict(),
            )

        return recent_expenses

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Unexpected error while retrieving recent expenses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=expense_unexpected_error_retrieve_recent(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.get(
    "/expenses",
    response_model=PagedExpense,
    responses={
        500: {"model": ErrorResponse},
    },
)
async def list_expenses_endpoint(
    db: AsyncSession = Depends(get_db),
    params: Params = Depends(),
    search: Optional[str] = None,
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
) -> PagedExpense:
    """
    Retrieve expenses with pagination, filtering, and sorting.
    Args:
        db (AsyncSession): The database session.
        params (Params): Pagination parameters.
        subject (Optional[str]): Filter by subject.
        expense_date (Optional[date]): Filter by expense date.
        reimbursable (Optional[bool]): Filter by reimbursable.
        employee (Optional[str]): Filter by employee name.
        sort_order (str): Sort order for expense_date, either 'asc' or 'desc'.
    Returns:
        PagedExpense: A paginated, filtered, and sorted response containing expenses.
    """
    try:
        logger.info("Fetching expenses with pagination, filtering, and sorting")
        paginated_expenses = await get_expenses(
            db=db,
            params=params,
            search=search,
            sort_order=sort_order,
        )
        return paginated_expenses
    except Exception as e:
        logger.error(f"Unexpected error while retrieving expenses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=expense_unexpected_error_list(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.get(
    "/expenses/all",
    response_model=List[ExpenseSchema],
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def fetch_all_expenses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ExpenseSchema]:
    """
    Retrieve expenses.
    Args:
        db (AsyncSession): The database session.
    Returns:
        List[ExpenseSchema]: Retrieves all expenses for the purpose of exporting all records.
    """
    try:
        expenses = await get_all_expenses(db)
        if not expenses:
            logger.warning("No expenses found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorResponse(
                    detail=expenses_not_found(),
                    status_code=status.HTTP_404_NOT_FOUND,
                ).dict(),
            )
        logger.info("Fetched all expenses.")
        return expenses
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error while retrieving expenses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=expense_unexpected_error_list(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.get(
    "/expenses/general-summary",
    response_model=GeneralSummary,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def get_general_summary_endpoint(
    year: int = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GeneralSummary:
    """
    Endpoint to retrieve general summary of expenses.
    Optionally specify a year for historical data.
    Args:
        year (int, optional): The year for which to retrieve the summary. Defaults to the most recent year with data.
    Returns:
        GeneralSummary: A summary of expense data.
    """
    try:
        available_years = await get_available_years(db)
        if not available_years:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No expense data available.",
            )
        if year is None:
            year = available_years[0]  # Most recent year
        elif year not in available_years:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No data available for year {year}",
            )
        return await get_general_summary_data(db, year)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error while retrieving general summary for year {year}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=general_summary_unexpected_error(year),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.get(
    "/expenses/last_5_months",
    response_model=list[dict],
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_last_5_months_summary_endpoint(
    year: int = Query(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[dict]:
    """
    Get the last 5 months summary for a specific year.

    Args:
        year (int): The year for which the data is required.

    Returns:
        list[dict]: The list of monthly totals.
    """
    try:
        logger.info(f"Fetching last 5 months summary for year: {year}")
        result = await get_last_5_months_summary(db, year)

        # Explicitly check if the result is empty or None and raise a 404 error
        if not result:
            logger.warning(f"No data found for year: {year}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for year {year}",
            )

        return result

    except HTTPException as http_exc:
        # If an HTTPException is already raised (like 404), re-raise it
        raise http_exc

    except Exception as e:
        # Catch all other exceptions and return 500 error
        logger.error(f"Unexpected error while fetching summary for year {year}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while retrieving the last 5 months summary for year {year}",
        ) from e


@router.get(
    "/expenses/by-category",
    response_model=list[dict],
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_expenses_by_category_endpoint(
    year: int = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """
    Endpoint to retrieve expenses grouped by category for a specific year.
    Optionally specify a year for historical data.
    Args:
        year (int, optional): The year for which to retrieve the expenses. Defaults to the most recent year with data.
    Returns:
        list[dict]: A list of dictionaries containing category names and total expenses.
    """
    try:
        available_years = await get_available_years(db)
        if not available_years:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No expense data available.",
            )
        if year is None:
            year = available_years[0]  # Most recent year
        elif year not in available_years:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No data available for year {year}",
            )
        return await get_expenses_by_category(db, year)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error while retrieving expenses by category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail="An unexpected error occurred while retrieving expenses by category.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.get(
    "/expenses/{expense_id}",
    response_model=ExpenseSchema,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_expense_endpoint(
    expense_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExpenseSchema:
    """
    Retrieve an expense by ID.

    Args:
        expense_id (UUID): The ID of the expense to retrieve.
        db (Session): The database session.

    Returns:
        ExpenseSchema: The retrieved expense object.
    """
    try:
        logger.info(f"Fetching expense with ID: {expense_id}")
        db_expense = await get_expense_by_id(db, expense_id)
        return ExpenseSchema.from_orm(db_expense)
    except ValueError as e:
        logger.error(f"Error retrieving expense with ID {expense_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                detail=expense_not_found(expense_id),
                status_code=status.HTTP_404_NOT_FOUND,
            ).dict(),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while retrieving expense with ID {expense_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=expense_unexpected_error_retrieve_by_id(expense_id),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.put(
    "/expenses/{expense_id}",
    response_model=ExpenseSchema,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def update_expense_endpoint(
    expense_id: UUID,
    expense_update: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    invoice_image: Optional[UploadFile] = File(None),
) -> ExpenseSchema:
    """
    Update an existing expense.
    Args:
        expense_id (UUID): The ID of the expense to update.
        expense_update (str): JSON string of the updated expense data.
        current_user (User): The current authenticated user.
        db (AsyncSession): The database session.
        invoice_image (UploadFile, optional): The invoice image file.
    Returns:
        ExpenseSchema: The updated expense object.
    """
    try:
        expense_update_data = json.loads(expense_update)
        expense_update_obj = ExpenseUpdate(**expense_update_data)
        logger.info(f"Attempting to update expense with ID: {expense_id}")
        db_expense = await update_expense(db, expense_id, expense_update_obj, invoice_image)
        return ExpenseSchema.from_orm(db_expense)
    except ValueError as e:
        logger.error(f"Error updating expense with ID {expense_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                detail=expense_update_not_found(expense_id),
                status_code=status.HTTP_404_NOT_FOUND,
            ).dict(),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while updating expense with ID {expense_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=expense_unexpected_error_update(expense_id),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.delete(
    "/expenses/{expense_id}",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def delete_expense_endpoint(
    expense_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete an expense by ID.

    Args:
        expense_id (UUID): The ID of the expense to delete.
        db (Session): The database session.

    Returns:
        dict: A message indicating the result of the deletion.
    """
    try:
        logger.info(f"Attempting to delete expense with ID: {expense_id}")
        result = await delete_expense(db, expense_id)
        return {"message": "Expense deleted successfully", "result": result}
    except ValueError as e:
        logger.error(f"Error deleting expense with ID {expense_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                detail=expense_deletion_not_found(expense_id),
                status_code=status.HTTP_404_NOT_FOUND,
            ).dict(),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while deleting expense with ID {expense_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=expense_unexpected_error_delete(expense_id),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


add_pagination(router)
