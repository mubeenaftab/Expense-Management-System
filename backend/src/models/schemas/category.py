"""
This module defines Pydantic schemas for category-related operations.
"""

from uuid import UUID

from fastapi_pagination import Page
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """
    Schema representing the base fields for creating and updating a category.

    Attributes:
        name (str): Name of the category.
    """

    name: str = Field(..., min_length=2, max_length=50)
    is_active: bool = Field(default=True)


class CategoryCreate(CategoryBase):
    """
    Schema representing the fields required to create a new category.
    Inherits: CategoryBase: Base schema with common category fields.
    """


class CategoryUpdate(CategoryBase):
    """
    Schema representing the fields required to update a category.
    Inherits: CategoryBase: Base schema with common category fields.
    """


class Category(CategoryBase):
    """
    Schema representing a category with a unique identifier.

    Attributes:
        category_id (UUID): Unique identifier for the category.
    """

    category_id: UUID

    class Config:
        """Configuration for the Pydantic model."""

        from_attributes = True


PagedCategory = Page[Category]
