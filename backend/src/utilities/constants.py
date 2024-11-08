from enum import Enum


class ErrorMessages(Enum):
    """
    Enum class to define common error messages used throughout the application.

    Attributes:
        ERROR_CREATING_USER (str): Message indicating that there was an error creating a user, typically because the username already exists.
        INVALID_CREDENTIALS (str): Message indicating that the provided credentials are invalid.
        ERROR_LOGGING_IN (str): Message indicating that an error occurred during the login process.
    """

    ERROR_CREATING_USER = "User already exists"
    INVALID_CREDENTIALS = "Credentials are invalid"
    ERROR_LOGGING_IN = "Error logging in"

    ERROR_CREATING_CATEGORY = "Error Creating Category"
    CATEGORY_NOT_FOUND = "Category not found!"
    CATEGORY_ALREADY_EXISTS = "Category already exist"
    ERROR_RETRIEVING_CATEGORY = "Error retrieving category"
    ERROR_RETRIEVING_CATEGORIES = "Error retrieving categories"
    ERROR_UPDATING_CATEGORY = "Error updating categories"
    ERROR_DELETING_CATEGORY = "Error deleting category"
