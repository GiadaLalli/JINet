"""Add a created timestamp to the usertoken table

Revision ID: 322b53bd2dbc
Revises: ec56daf309a6
Create Date: 2024-06-28 13:37:46.870071

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "322b53bd2dbc"
down_revision: Union[str, None] = "ec56daf309a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usertoken", sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=True)
    )

    op.execute("UPDATE usertoken SET created = CURRENT_TIMESTAMP")

    op.alter_column("usertoken", "created", nullable=False)


def downgrade() -> None:
    op.drop_column("usertoken", "created")
