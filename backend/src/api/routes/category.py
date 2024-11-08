from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import add_pagination, Page, paginate, Params
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.config.settings.logger_config import logger
from src.models.schemas.category import Category as CategorySchema, CategoryCreate, CategoryUpdate, PagedCategory
from src.models.schemas.error_response import ErrorResponse
from src.repository.crud.category import (
    create_category,
    get_active_categories,
    get_categories,
    get_category_by_id,
    get_category_by_name,
    mark_category_as_inactive,
    update_category,
)
from src.repository.database import get_db
from src.utilities.messages.exceptions.http.exc_details import (
    category_deletion_not_found,
    category_exists,
    category_not_found,
    category_not_found_by_name,
    category_update_not_found,
    unexpected_error_create,
    unexpected_error_delete,
    unexpected_error_list,
    unexpected_error_retrieve_by_id,
    unexpected_error_retrieve_by_name,
    unexpected_error_update,
)

router = APIRouter()


@router.post(
    "/categories",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def create_category_endpoint(category: CategoryCreate, db: AsyncSession = Depends(get_db)) -> CategorySchema:
    """
    Create a new category.

    Args:
        category (CategoryCreate): The category data to create.
        db (Session): The database session.

    Returns:
        CategorySchema: The created category object.
    """
    try:
        logger.info(f"Attempting to create a new category with name: {category.name}")

        existing_category = await get_category_by_name(db, category.name)
        if existing_category:
            logger.warning(f"Category with name '{category.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    detail=category_exists(category.name),
                    status_code=status.HTTP_400_BAD_REQUEST,
                ).dict(),
            )

        db_category = await create_category(db, category)
        logger.info(f"Category created successfully with ID: {db_category.category_id}")
        return CategorySchema.from_orm(db_category)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during category creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=unexpected_error_create(category.name),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.get(
    "/categories/active",
    response_model=list[CategorySchema],
    responses={
        500: {"model": ErrorResponse},
    },
)
async def list_active_categories_endpoint(db: AsyncSession = Depends(get_db)) -> list[CategorySchema]:
    """
    Retrieve all active categories.

    Args:
        db (Session): The database session.

    Returns:
        list[CategorySchema]: A list of active category objects.
    """
    try:
        logger.info("Fetching all active categories")
        categories = await get_active_categories(db)
        logger.info(f"Total active categories retrieved: {len(categories)}")
        return [CategorySchema.from_orm(category) for category in categories]
    except Exception as e:
        logger.error(f"Unexpected error while retrieving active categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=unexpected_error_list(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.get(
    "/categories/{category_id}",
    response_model=CategorySchema,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_category_endpoint(category_id: UUID, db: AsyncSession = Depends(get_db)) -> CategorySchema:
    """
    Retrieve a category by ID.

    Args:
        category_id (UUID): The ID of the category to retrieve.
        db (Session): The database session.

    Returns:
        CategorySchema: The retrieved category object.
    """
    try:
        logger.info(f"Fetching category with ID: {category_id}")
        db_category = await get_category_by_id(db, category_id)
        return CategorySchema.from_orm(db_category)
    except ValueError as e:
        logger.error(f"Error retrieving category with ID {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                detail=category_not_found(category_id),
                status_code=status.HTTP_404_NOT_FOUND,
            ).dict(),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while retrieving category with ID {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=unexpected_error_retrieve_by_id(category_id),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.get(
    "/categories",
    response_model=PagedCategory,
    responses={
        500: {"model": ErrorResponse},
    },
)
async def list_categories_endpoint(
    db: AsyncSession = Depends(get_db),
    params: Params = Depends(),
) -> PagedCategory:
    """
    Retrieve categories with pagination.

    Args:
        db (AsyncSession): The database session.
        params (Params): Pagination parameters.

    Returns:
        PagedCategory: A paginated response containing categories.
    """
    try:
        logger.info("Fetching categories with pagination")
        categories = await get_categories(db)
        return paginate(categories, params)
    except Exception as e:
        logger.error(f"Unexpected error while retrieving categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=unexpected_error_list(),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.get(
    "/categories/by-name/{name}",
    response_model=CategorySchema,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_category_by_name_endpoint(name: str, db: AsyncSession = Depends(get_db)) -> CategorySchema:
    """
    Retrieve a category by name.

    Args:
        name (str): The name of the category to retrieve.
        db (Session): The database session.

    Returns:
        CategorySchema: The retrieved category object.
    """
    try:
        logger.info(f"Fetching category with name: {name}")
        db_category = await get_category_by_name(db, name)
        return CategorySchema.from_orm(db_category)
    except ValueError as e:
        logger.error(f"Error retrieving category with name '{name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                detail=category_not_found_by_name(name),
                status_code=status.HTTP_404_NOT_FOUND,
            ).dict(),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while retrieving category with name '{name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=unexpected_error_retrieve_by_name(name),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.put(
    "/categories/{category_id}",
    response_model=CategorySchema,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def update_category_endpoint(
    category_id: UUID, category_update: CategoryUpdate, db: AsyncSession = Depends(get_db)
) -> CategorySchema:
    """
    Update an existing category.

    Args:
        category_id (UUID): The ID of the category to update.
        category_update (CategoryUpdate): The updated category data.
        db (Session): The database session.

    Returns:
        CategorySchema: The updated category object.
    """
    try:
        logger.info(f"Attempting to update category with ID: {category_id}")
        db_category = await update_category(db, category_id, category_update)
        return CategorySchema.from_orm(db_category)
    except ValueError as e:
        logger.error(f"Error updating category with ID {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                detail=category_update_not_found(category_id),
                status_code=status.HTTP_404_NOT_FOUND,
            ).dict(),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while updating category with ID {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=unexpected_error_update(category_id),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.patch(
    "/categories/{category_id}",
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def mark_category_as_inactive_endpoint(category_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """
    Mark a category Inactive by ID.

    Args:
        category_id (UUID): The ID of the category to delete.
        db (Session): The database session.

    Returns:
        dict: A message indicating the result of the inactive.
    """
    try:
        logger.info(f"Attempting to delete category with ID: {category_id}")
        result = await mark_category_as_inactive(db, category_id)
        return {"message": "Category inactived successfully", "result": result}
    except ValueError as e:
        logger.error(f"Error marking category inactive with ID {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                detail=category_deletion_not_found(category_id),
                status_code=status.HTTP_404_NOT_FOUND,
            ).dict(),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error while marking category inactive with ID {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=unexpected_error_delete(category_id),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


add_pagination(router)
