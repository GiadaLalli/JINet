"""Create sharedata table.

Revision ID: 423bb8d38355
Revises: a86ddc120024
Create Date: 2024-05-13 09:34:20.645856

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "423bb8d38355"
down_revision: Union[str, None] = "a86ddc120024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sharedata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reference", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("output", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("filename", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("checksum", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("data", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("created", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["package_id"],
            ["package.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("sharedata")
