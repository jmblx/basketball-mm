"""empty message

Revision ID: 4225b580c34d
Revises: 33dfa957dfec
Create Date: 2024-01-11 23:56:28.398621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4225b580c34d'
down_revision: Union[str, None] = '33dfa957dfec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('match', sa.Column('loser_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'match', 'team', ['loser_id'], ['id'])
    op.add_column('match_5x5', sa.Column('winner_id', sa.Integer(), nullable=True))
    op.add_column('match_5x5', sa.Column('loser_id', sa.Integer(), nullable=True))
    op.drop_constraint('match_5x5_winner_team_id_fkey', 'match_5x5', type_='foreignkey')
    op.create_foreign_key(None, 'match_5x5', 'team', ['loser_id'], ['id'])
    op.create_foreign_key(None, 'match_5x5', 'team', ['winner_id'], ['id'])
    op.drop_column('match_5x5', 'winner_team_id')
    op.add_column('solomatch', sa.Column('loser_id', sa.Integer(), nullable=True))
    op.alter_column('solomatch', 'winner_id',
               existing_type=sa.UUID(),
               type_=sa.Integer(),
               existing_nullable=True)
    op.drop_constraint('solomatch_winner_id_fkey', 'solomatch', type_='foreignkey')
    op.create_foreign_key(None, 'solomatch', 'team', ['winner_id'], ['id'])
    op.create_foreign_key(None, 'solomatch', 'team', ['loser_id'], ['id'])
    op.add_column('team', sa.Column('rating_5x5', sa.Integer(), nullable=False))
    op.add_column('team', sa.Column('match5x5_wins', sa.Integer(), nullable=True))
    op.add_column('team', sa.Column('match5x5_loses', sa.Integer(), nullable=True))
    op.add_column('team', sa.Column('match5x5_winrate', sa.Float(), nullable=True))
    op.add_column('team', sa.Column('match5x5_played', sa.Integer(), nullable=True))
    op.drop_column('team', 'rating')
    op.add_column('user', sa.Column('match5x5_wins', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('match5x5_loses', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('match5x5_winrate', sa.Float(), nullable=True))
    op.add_column('user', sa.Column('match5x5_played', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'match5x5_played')
    op.drop_column('user', 'match5x5_winrate')
    op.drop_column('user', 'match5x5_loses')
    op.drop_column('user', 'match5x5_wins')
    op.add_column('team', sa.Column('rating', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('team', 'match5x5_played')
    op.drop_column('team', 'match5x5_winrate')
    op.drop_column('team', 'match5x5_loses')
    op.drop_column('team', 'match5x5_wins')
    op.drop_column('team', 'rating_5x5')
    op.drop_constraint(None, 'solomatch', type_='foreignkey')
    op.drop_constraint(None, 'solomatch', type_='foreignkey')
    op.create_foreign_key('solomatch_winner_id_fkey', 'solomatch', 'user', ['winner_id'], ['id'])
    op.alter_column('solomatch', 'winner_id',
               existing_type=sa.Integer(),
               type_=sa.UUID(),
               existing_nullable=True)
    op.drop_column('solomatch', 'loser_id')
    op.add_column('match_5x5', sa.Column('winner_team_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'match_5x5', type_='foreignkey')
    op.drop_constraint(None, 'match_5x5', type_='foreignkey')
    op.create_foreign_key('match_5x5_winner_team_id_fkey', 'match_5x5', 'team', ['winner_team_id'], ['id'])
    op.drop_column('match_5x5', 'loser_id')
    op.drop_column('match_5x5', 'winner_id')
    op.drop_constraint(None, 'match', type_='foreignkey')
    op.drop_column('match', 'loser_id')
    # ### end Alembic commands ###
