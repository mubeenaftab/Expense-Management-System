from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings.logger_config import logger
from src.models.schemas.auth_schema import Token
from src.models.schemas.error_response import ErrorResponse
from src.models.schemas.user import User as UserSchema, UserCreate
from src.repository.crud.user import authenticate_user, create_user
from src.repository.database import get_db
from src.securities.authorization.jwt import create_access_token
from src.utilities.constants import ErrorMessages

router = APIRouter()


@router.post(
    "/register",
    response_model=UserSchema,
    responses={
        500: {"model": ErrorResponse},
    },
)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> UserSchema:
    """
    Register a new user.

    Args:
        user (UserCreate): The user data for registration.
        db (Session): The database session.

    Returns:
        UserSchema: The registered user.

    Raises:
        HTTPException: If there's an error during user creation.
    """
    try:
        logger.info(f"Attempting to register user with username: {user.username}")
        db_user = await create_user(db, user)
        logger.info(f"User registered successfully with ID: {db_user.user_id}")
        return UserSchema.from_orm(db_user)
    except Exception as e:
        logger.error(f"Unexpected error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=ErrorMessages.ERROR_CREATING_USER.value,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e


@router.post(
    "/login",
    response_model=Token,
    responses={
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> Token:
    """
    Authenticate a user and provide an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing username and password for authentication.
        db (Session): The database session used to validate user credentials.

    Returns:
        Token: A JWT access token for the authenticated user.

    Raises:
        HTTPException: If authentication fails due to invalid credentials or other errors.
    """
    try:
        logger.info("Attempting to authenticate user ")
        user = await authenticate_user(db, form_data.username, form_data.password)

        if not user:
            logger.warning("Invalid credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorResponse(
                    detail=ErrorMessages.INVALID_CREDENTIALS.value,
                    status_code=status.HTTP_401_UNAUTHORIZED,
                ).dict(),
            )

        access_token = await create_access_token(data={"sub": user.username})
        logger.info(f"User authenticated successfully {user.username}")
        return Token(access_token=access_token, token_type="bearer")

    except HTTPException as e:
        logger.error(f"HTTP exception occurred: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                detail=ErrorMessages.ERROR_LOGGING_IN.value,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ).dict(),
        ) from e
