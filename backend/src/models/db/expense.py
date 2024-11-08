import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, Float, ForeignKey, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.repository.database import Base


class Expense(Base):
    """
    Represents an expense in the system.
    """

    __tablename__ = "expenses"

    expenses_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    category_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("category.category_id"), nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reimbursable: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    invoice_image: Mapped[str] = mapped_column(String, nullable=True)
    employee: Mapped[str] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
