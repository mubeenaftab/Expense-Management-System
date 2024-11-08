"""
This module defines Pydantic schemas for user-related data.

These schemas are used for validating and serializing user data, such as
user creation, login, and profile information, within the FastAPI application.

Imports:
    - BaseModel from Pydantic for creating data validation and serialization models.
    - EmailStr from Pydantic for validating email addresses.
    - UUID4 from Pydantic for handling UUID fields.
    - Optional from typing for defining optional fields.
"""

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, UUID4


class UserBase(BaseModel):
    """
    Base schema for user data, used as a base class for other user schemas.

    Attributes:
        username (str): The username of the user.

    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=80,
        description="Username must be between 3 and 80 characters long",
    )


class UserCreate(UserBase):
    """
    Schema for user creation, extending the base user schema.

    Attributes:
        password (str): The password for the user account.
    """

    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        """
        Validates the password to ensure it meets complexity requirements.

        Args:
            password (str): The password for the user account.

        Returns:
            str: The validated password if it meets the requirements.

        Raises:
            ValueError: If the password does not meet the complexity requirements.
        """
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")
        return password


class User(UserBase):
    """
    Schema for a user profile, extending the base user schema.

    Attributes:
        id (UUID4): The unique identifier for the user.
        is_active (bool): Indicates whether the user account is active.
    """

    user_id: UUID4
    is_active: bool
    timestamp: datetime

    class Config:
        """
        Configuration for the Pydantic model.

        Enables compatibility with ORM models by allowing the model to
        be populated from attributes of an ORM model instance.
        """

        from_attributes = True
