"""initial migration

Revision ID: 24ab0d024d1c
Revises:
Create Date: 2024-09-19 18:53:18.588080

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "24ab0d024d1c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "category",
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("category_id"),
    )
    op.create_index(op.f("ix_category_category_id"), "category", ["category_id"], unique=False)
    op.create_index(op.f("ix_category_name"), "category", ["name"], unique=True)
    op.create_table(
        "users",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("timestamp", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_table(
        "expenses",
        sa.Column("expenses_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("reimbursable", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("invoice_image", sa.String(), nullable=True),
        sa.Column("employee", sa.String(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["category.category_id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("expenses_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("expenses")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_category_name"), table_name="category")
    op.drop_index(op.f("ix_category_category_id"), table_name="category")
    op.drop_table("category")
    # ### end Alembic commands ###
