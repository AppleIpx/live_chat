"""add null for content message

Revision ID: 0c4adf5ddab8
Revises: 269c383405c1
Create Date: 2024-12-18 08:28:50.706373

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0c4adf5ddab8"
down_revision = "269c383405c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "deleted_message",
        "content",
        existing_type=sa.VARCHAR(length=5000),
        nullable=True,
    )
    op.alter_column(
        "message", "content", existing_type=sa.VARCHAR(length=5000), nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "message", "content", existing_type=sa.VARCHAR(length=5000), nullable=False
    )
    op.alter_column(
        "deleted_message",
        "content",
        existing_type=sa.VARCHAR(length=5000),
        nullable=False,
    )
    # ### end Alembic commands ###
