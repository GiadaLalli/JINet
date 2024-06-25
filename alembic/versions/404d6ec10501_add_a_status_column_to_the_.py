"""Add a status column to the permissionrequest table

Revision ID: 404d6ec10501
Revises: 423bb8d38355
Create Date: 2024-06-25 09:52:54.104389

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "404d6ec10501"
down_revision: Union[str, None] = "423bb8d38355"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "permissionrequest",
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )

    op.execute("UPDATE permissionrequest SET status = 'requested'")

    op.alter_column("permissionrequest", "status", nullable=False)


def downgrade() -> None:
    op.drop_column("permissionrequest", "status")
