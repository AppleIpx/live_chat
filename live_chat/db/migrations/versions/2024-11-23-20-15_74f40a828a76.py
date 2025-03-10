"""add chat name

Revision ID: 74f40a828a76
Revises: dde630e0f286
Create Date: 2024-11-23 20:15:51.624769

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "74f40a828a76"
down_revision = "dde630e0f286"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("chat", sa.Column("name", sa.String(length=50), nullable=True))
    op.add_column("chat", sa.Column("image", sa.String(length=1048), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("chat", "image")
    op.drop_column("chat", "name")
    # ### end Alembic commands ###
