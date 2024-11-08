import uuid

from sqlalchemy import Boolean, Column, String, text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.repository.database import Base


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        user_id (UUID): Unique identifier for the user, automatically generated.
        username (str): The username of the user. Must be unique and cannot be null.
        hashed_password (str): The hashed password for the user. Cannot be null.
        is_active (bool): Flag indicating whether the user account is active. Defaults to True.

    Table:
        - `users`: The table name in the database where user information is stored.

    This class is mapped to the `users` table in the database and is used to manage user-related data.
    """

    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    timestamp = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    expenses = relationship("Expense", back_populates="user")
