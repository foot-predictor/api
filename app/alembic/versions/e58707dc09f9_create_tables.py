"""Create tables

Revision ID: e58707dc09f9
Revises:
Create Date: 2025-01-01 21:42:37.149662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = 'e58707dc09f9'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('competition',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type_', sa.String(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('place_code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('place_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('logo_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('data_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('stats_id', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('data_id'),
    sa.UniqueConstraint('stats_id')
    )
    op.create_table('team',
    sa.Column('short_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('tag', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('city', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('venue_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('logo_url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('data_id', sa.Integer(), nullable=False),
    sa.Column('stats_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('data_id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('stats_id')
    )
    op.create_table('competitionteamlink',
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('competition_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['competition_id'], ['competition.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['team_id'], ['team.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('team_id', 'competition_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('competitionteamlink')
    op.drop_table('team')
    op.drop_table('competition')
    # ### end Alembic commands ###
