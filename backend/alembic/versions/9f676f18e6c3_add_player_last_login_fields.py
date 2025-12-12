"""Add player last_login fields

Revision ID: 9f676f18e6c3
Revises: dae9bca9970a
Create Date: 2025-12-12 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f676f18e6c3"
down_revision: Union[str, None] = "dae9bca9970a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "players",
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "players",
        sa.Column("login_count", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("players", "login_count")
    op.drop_column("players", "last_login_at")
