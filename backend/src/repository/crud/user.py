from typing import Optional

import pendulum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config.settings.base import TZ
from src.config.settings.logger_config import logger
from src.models.db.user import User as UserModel
from src.models.schemas.user import UserCreate
from src.securities.hashing.hash import get_password_hash, verify_password


async def create_user(db: AsyncSession, user: UserCreate) -> UserModel:
    """
    Creates a new user in the database.

    Args:
        db (AsyncSession): The database session.
        user (UserCreate): The user data to create.

    Returns:
        UserModel: The created user object.

    Raises:
        ValueError: If the username already exists.
    """
    timezone = pendulum.timezone(TZ)
    try:
        hashed_password = await get_password_hash(user.password)
        db_user = UserModel(
            username=user.username,
            hashed_password=hashed_password,
            timestamp=pendulum.now(tz=timezone).naive(),  # Set the timestamp
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"User created successfully with username: {user.username}")
        return db_user

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[UserModel]:
    """
    Authenticates a user by verifying the username and password.

    Args:
        db (AsyncSession): The database session.
        username (str): The user's username.
        password (str): The user's password.

    Returns:
        Optional[UserModel]: The authenticated user object, or None if authentication fails.
    """
    try:
        # Query the database for the user with the provided username
        stmt = select(UserModel).filter(UserModel.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()  # Fetch a single user or None

        if user is None or not await verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed for username: {username}")
            return None

        logger.info(f"User authenticated successfully with username: {username}")
        return user

    except Exception as e:
        logger.error(f"Error during user authentication: {e}")
        raise
