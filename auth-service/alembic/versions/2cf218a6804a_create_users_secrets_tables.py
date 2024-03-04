"""create Users, Secrets tables

Revision ID: 2cf218a6804a
Revises: 
Create Date: 2024-03-03 23:06:23.140731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cf218a6804a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('secrets',
    sa.Column('secret', sa.UUID(), nullable=False),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('used_by', sa.UUID(), nullable=True),
    sa.Column('is_used', sa.Boolean(), server_default='false', nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('secret')
    )
    op.create_table('users',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('login', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('surname', sa.String(), nullable=False),
    sa.Column('used_secret', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['used_secret'], ['secrets.secret'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('login')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('secrets')
    # ### end Alembic commands ###