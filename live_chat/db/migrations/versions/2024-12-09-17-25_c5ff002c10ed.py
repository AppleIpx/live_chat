"""change models fields

Revision ID: c5ff002c10ed
Revises: 97b1e7bdc4ee
Create Date: 2024-12-09 17:25:08.425842

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c5ff002c10ed"
down_revision = "97b1e7bdc4ee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "read_status",
        sa.Column("count_unread_msg", sa.Integer(), nullable=True),
    )
    op.execute(
        "UPDATE read_status SET count_unread_msg = 0 WHERE count_unread_msg IS NULL"
    )
    op.alter_column("read_status", "count_unread_msg", nullable=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("read_status", "count_unread_msg")
    # ### end Alembic commands ###
