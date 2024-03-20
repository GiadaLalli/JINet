"""Add table for sample data

Revision ID: 87916e77b6ed
Revises: 992b5dcdead1
Create Date: 2024-03-14 14:01:33.850333

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "87916e77b6ed"
down_revision: Union[str, None] = "992b5dcdead1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sampledata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("mime", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "permissionrequest",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("permission", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("permission", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("sampledata")
    op.drop_table("permissionrequest")
