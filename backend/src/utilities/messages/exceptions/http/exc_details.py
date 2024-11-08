from typing import Optional
from uuid import UUID


def category_not_found(category_id: UUID) -> str:
    return f"No category found with ID '{category_id}'. Please check the ID and try again."


def category_not_found_by_name(name: str) -> str:
    return f"No category found with the name '{name}'. Please check the name and try again."


def category_exists(name: str) -> str:
    return f"Category with name '{name}' already exists. Please choose a different name."


def category_update_not_found(category_id: UUID) -> str:
    return f"No category found with ID '{category_id}' for update. Please check the ID and try again."


def category_deletion_not_found(category_id: UUID) -> str:
    return f"No category found with ID '{category_id}' for deletion. Please check the ID and try again."


def unexpected_error_create(name: str) -> str:
    return f"An unexpected error occurred while creating the category '{name}'. Please try again later."


def unexpected_error_retrieve_by_id(category_id: UUID) -> str:
    return (
        f"An unexpected error occurred while retrieving the category with ID '{category_id}'. Please try again later."
    )


def unexpected_error_retrieve_by_name(name: str) -> str:
    return f"An unexpected error occurred while retrieving the category with name '{name}'. Please try again later."


def unexpected_error_update(category_id: UUID) -> str:
    return f"An unexpected error occurred while updating the category with ID '{category_id}'. Please try again later."


def unexpected_error_delete(category_id: UUID) -> str:
    return f"An unexpected error occurred while deleting the category with ID '{category_id}'. Please try again later."


def unexpected_error_list() -> str:
    return "An unexpected error occurred while retrieving the list of categories. Please try again later."


### Details for Expenses
def expense_not_found(expense_id: UUID) -> str:
    return f"No expense found with ID '{expense_id}'. Please check the ID and try again."


def expense_exists(name: str) -> str:
    return f"Expense with name '{name}' already exists. Please choose a different name."


def expense_update_not_found(expense_id: UUID) -> str:
    return f"No expense found with ID '{expense_id}' for update. Please check the ID and try again."


def expense_deletion_not_found(expense_id: UUID) -> str:
    return f"No expense found with ID '{expense_id}' for deletion. Please check the ID and try again."


def expense_unexpected_error_create(subject: str) -> str:
    return f"An unexpected error occurred while creating the expense '{subject}'. Please try again later."


def expense_unexpected_error_retrieve_by_id(expense_id: UUID) -> str:
    return f"An unexpected error occurred while retrieving the expense with ID '{expense_id}'. Please try again later."


def expense_unexpected_error_retrieve_by_name(name: str) -> str:
    return f"An unexpected error occurred while retrieving the expense with name '{name}'. Please try again later."


def expense_unexpected_error_update(expense_id: UUID) -> str:
    return f"An unexpected error occurred while updating the expense with ID '{expense_id}'. Please try again later."


def expense_unexpected_error_delete(expense_id: UUID) -> str:
    return f"An unexpected error occurred while deleting the expense with ID '{expense_id}'. Please try again later."


def expense_unexpected_error_list() -> str:
    return "An unexpected error occurred while retrieving the list of expenses. Please try again later."


def expense_recent_not_found() -> str:
    return "No recent expenses found. Please check your data or try again later."


def expense_unexpected_error_retrieve_recent() -> str:
    return "An unexpected error occurred while retrieving the recent expenses. Please try again later."


def expenses_not_found() -> str:
    return "No expenses found. Please enter expense and try again."


def expenses_by_category_unexpected_error() -> str:
    return "An unexpected error occurred while retrieving expenses by category. Please try again later."


def expense_summary_not_found_for_year(year: int) -> str:
    return f"No data found for year '{year}'. Please check the year and try again."


def expense_unexpected_error_retrieve_summary_by_year(year: int) -> str:
    return f"An unexpected error occurred while retrieving the last 5 months summary for year '{year}'. Please try again later."


def expense_invalid_year_format(year: int) -> str:
    return f"Invalid year format '{year}'. Please provide a valid year and try again."


def available_years_unexpected_error() -> str:
    return "An unexpected error occurred while retrieving available years. Please try again later."


def general_summary_unexpected_error(year: Optional[int] = None) -> str:
    if year:
        return f"An unexpected error occurred while retrieving the general summary for year {year}. Please try again later."
    return "An unexpected error occurred while retrieving the general summary. Please try again later."
