import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.repository.database import Base


class Category(Base):  # type: ignore
    """
    Represents a category in the database.

    Attributes:
        category_id (UUID): The unique identifier for the category.
        name (str): The name of the category, which must be unique.
    """

    __tablename__ = "category"

    category_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    expenses = relationship("Expense", back_populates="category")
