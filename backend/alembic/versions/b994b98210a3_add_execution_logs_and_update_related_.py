"""Add execution logs and update related tables

Revision ID: b994b98210a3
Revises: 6bf4c6aeb826
Create Date: 2024-12-06 18:31:23.762828

"""
from typing import Sequence, Text, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import String

# revision identifiers, used by Alembic.
revision: str = 'b994b98210a3'
down_revision: Union[str, None] = '6bf4c6aeb826'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('execution_logs',
    sa.Column('status', sa.Enum('SUCCESS', 'FAILED', 'PENDING', 'RUNNING', native_enum=False), nullable=False),
    sa.Column('query_id', sa.Uuid(), nullable=False),
    sa.Column('executed_by', sa.String(), nullable=False),
    sa.Column('notify_to', postgresql.ARRAY(String()), nullable=False),
    sa.Column('logs', postgresql.JSONB(astext_type=Text()), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['executed_by'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['query_id'], ['sql_queries.sqid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('saved_queries', sa.Column('name', sa.String(), nullable=False))
    op.add_column('saved_queries', sa.Column('description', sa.String(), nullable=False))
    op.alter_column('saved_queries', 'turn_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.add_column('users', sa.Column('name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'email')
    op.drop_column('users', 'name')
    op.alter_column('saved_queries', 'turn_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('saved_queries', 'description')
    op.drop_column('saved_queries', 'name')
    op.drop_table('execution_logs')
    # ### end Alembic commands ###