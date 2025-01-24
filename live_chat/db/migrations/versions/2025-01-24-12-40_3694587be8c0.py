"""delete unique id in chat_participant

Revision ID: 3694587be8c0
Revises: 3f11db9a45e3
Create Date: 2025-01-24 12:40:43.348014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3694587be8c0'
down_revision = '3f11db9a45e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('chat_participant_pkey', 'chat_participant', type_='primary')

    op.alter_column('chat_participant', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('chat_participant', 'chat_id',
               existing_type=sa.UUID(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('chat_participant', 'chat_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('chat_participant', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)

    op.create_primary_key('chat_participant_pkey', 'chat_participant', ['user_id', 'chat_id'])
