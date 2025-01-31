"""change stats id by 2 new apis

Revision ID: 7469093c6155
Revises: e58707dc09f9
Create Date: 2025-01-19 10:24:56.390671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision: str = '7469093c6155'
down_revision: Union[str, None] = 'e58707dc09f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('competition', sa.Column('livescore_id', sa.Integer(), nullable=True))
    op.add_column('competition', sa.Column('transfermarkt_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.drop_constraint('competition_stats_id_key', 'competition', type_='unique')
    op.create_unique_constraint(None, 'competition', ['livescore_id'])
    op.create_unique_constraint(None, 'competition', ['transfermarkt_id'])
    op.drop_column('competition', 'stats_id')
    op.add_column('team', sa.Column('livescore_id', sa.Integer(), nullable=True))
    op.add_column('team', sa.Column('transfermarkt_id', sa.Integer(), nullable=True))
    op.drop_constraint('team_stats_id_key', 'team', type_='unique')
    op.create_unique_constraint(None, 'team', ['transfermarkt_id'])
    op.create_unique_constraint(None, 'team', ['livescore_id'])
    op.drop_column('team', 'stats_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('team', sa.Column('stats_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'team', type_='unique')
    op.drop_constraint(None, 'team', type_='unique')
    op.create_unique_constraint('team_stats_id_key', 'team', ['stats_id'])
    op.drop_column('team', 'transfermarkt_id')
    op.drop_column('team', 'livescore_id')
    op.add_column('competition', sa.Column('stats_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'competition', type_='unique')
    op.drop_constraint(None, 'competition', type_='unique')
    op.create_unique_constraint('competition_stats_id_key', 'competition', ['stats_id'])
    op.drop_column('competition', 'transfermarkt_id')
    op.drop_column('competition', 'livescore_id')
    # ### end Alembic commands ###
