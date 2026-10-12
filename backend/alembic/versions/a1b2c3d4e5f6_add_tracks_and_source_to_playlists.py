"""add tracks and source to playlists

Revision ID: a1b2c3d4e5f6
Revises: fafdf393aec2
Create Date: 2026-10-12 16:45:00

Stores the full track list (title, artist, links) so a playlist can be
displayed and replayed even without Spotify.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'fafdf393aec2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('playlists') as batch:
        batch.add_column(sa.Column('tracks', sa.JSON(), nullable=True))
        batch.add_column(sa.Column('source', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('playlists') as batch:
        batch.drop_column('source')
        batch.drop_column('tracks')
