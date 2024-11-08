from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.settings.logger_config import logger
from src.models.db.category import Category as CategoryModel
from src.models.schemas.category import CategoryCreate, CategoryUpdate


async def create_category(db: AsyncSession, category: CategoryCreate) -> CategoryModel:
    """
    Create a new category asynchronously.

    Args:
        db (AsyncSession): The database session.
        category (CategoryCreate): The category data to create.

    Returns:
        CategoryModel: The created category model.

    Raises:
        RuntimeError: If there is an error creating the category.
    """
    try:
        db_category = CategoryModel(name=category.name, is_active=category.is_active)
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        logger.info(f"Category created successfully with name: {category.name}")
        return db_category
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        raise RuntimeError("Error creating category") from e


async def get_category_by_id(db: AsyncSession, category_id: UUID) -> CategoryModel:
    """
    Retrieve a category by ID asynchronously.

    Args:
        db (AsyncSession): The database session.
        category_id (UUID): The ID of the category to retrieve.

    Returns:
        CategoryModel: The retrieved category model.

    Raises:
        ValueError: If the category is not found.
        RuntimeError: If there is an error retrieving the category.
    """
    try:
        query = select(CategoryModel).filter(CategoryModel.category_id == category_id)
        result = await db.execute(query)
        category = result.scalars().first()
        if not category:
            logger.warning(f"Category not found with ID: {category_id}")
            raise ValueError("Category not found")
        logger.info(f"Category retrieved successfully with ID: {category_id}")
        return category
    except ValueError as e:
        logger.error(f"Category retrieval error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error retrieving category with ID {category_id}: {e}")
        raise RuntimeError("Error retrieving category") from e


async def get_category_by_name(db: AsyncSession, name: str) -> Optional[CategoryModel]:
    """
    Retrieve a category by name asynchronously.

    Args:
        db (AsyncSession): The database session.
        name (str): The name of the category to retrieve.

    Returns:
        Optional[CategoryModel]: The retrieved category model, or None if not found.
    """
    try:
        query = select(CategoryModel).filter(CategoryModel.name == name)
        result = await db.execute(query)
        category = result.scalars().first()
        if category:
            logger.info(f"Category retrieved successfully with name: {name}")
        else:
            logger.info(f"No category found with name: {name}")
        return category
    except Exception as e:
        logger.error(f"Error retrieving category with name {name}: {e}")
        raise RuntimeError("Error retrieving category") from e


async def get_categories(db: AsyncSession) -> list[CategoryModel]:
    """
    Retrieve all categories asynchronously.

    Args:
        db (AsyncSession): The database session.

    Returns:
        list[CategoryModel]: The list of all category models.

    Raises:
        RuntimeError: If there is an error retrieving the categories.
    """
    try:
        query = select(CategoryModel)
        result = await db.execute(query)
        categories = result.scalars().all()
        logger.info(f"Total categories retrieved: {len(categories)}")
        return categories
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        raise RuntimeError("Error retrieving categories") from e


async def get_active_categories(db: AsyncSession) -> list[CategoryModel]:
    """
    Retrieve all active categories.
    Args:
        db (AsyncSession): The database session.
    Returns:
        list[Category]: List of active categories.
    """
    try:
        query = select(CategoryModel).filter(CategoryModel.is_active)
        result = await db.execute(query)
        categories = result.scalars().all()
        logger.info(f"Total categories retrieved: {len(categories)}")
        return categories
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        raise RuntimeError("Error retrieving categories") from e


async def update_category(db: AsyncSession, category_id: UUID, category_update: CategoryUpdate) -> CategoryModel:
    """
    Update a category by ID asynchronously.

    Args:
        db (AsyncSession): The database session.
        category_id (UUID): The ID of the category to update.
        category_update (CategoryUpdate): The category data to update.

    Returns:
        CategoryModel: The updated category model.

    Raises:
        ValueError: If the category is not found.
        RuntimeError: If there is an error updating the category.
    """
    try:
        query = select(CategoryModel).filter(CategoryModel.category_id == category_id)
        result = await db.execute(query)
        category = result.scalars().first()
        if not category:
            logger.warning(f"Category not found with ID: {category_id}")
            raise ValueError("Category not found")
        category.name = category_update.name
        category.is_active = category_update.is_active
        await db.commit()
        await db.refresh(category)
        logger.info(f"Category updated successfully with ID: {category_id}")
        return category
    except ValueError as e:
        logger.error(f"Category update error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error updating category with ID {category_id}: {e}")
        raise RuntimeError("Error updating category") from e


async def mark_category_as_inactive(db: AsyncSession, category_id: UUID) -> bool:
    """
    Mark a category as inactive by ID asynchronously.
    Args:
        db (AsyncSession): The database session.
        category_id (UUID): The ID of the category to update.
    Returns:
        bool: True if the category was marked as inactive successfully.
    Raises:
        ValueError: If the category is not found.
        RuntimeError: If there is an error updating the category.
    """
    try:
        query = select(CategoryModel).filter(CategoryModel.category_id == category_id)
        result = await db.execute(query)
        category = result.scalars().first()
        if not category:
            logger.warning(f"Category not found with ID: {category_id}")
            raise ValueError("Category not found")
        category.is_active = False
        await db.commit()
        logger.info(f"Category marked as inactive successfully with ID: {category_id}")
        return True
    except ValueError as e:
        logger.error(f"Category update error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error marking category as inactive with ID {category_id}: {e}")
        raise RuntimeError("Error updating category") from e
