"""Add short_description and logo columns to the package table

Revision ID: a86ddc120024
Revises: 87916e77b6ed
Create Date: 2024-04-03 14:13:08.092638

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "a86ddc120024"
down_revision: Union[str, None] = "87916e77b6ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION pg_trgm;"))
    op.add_column(
        "package",
        sa.Column(
            "short_description", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column("package", sa.Column("logo", sa.LargeBinary(), nullable=True))
    op.add_column(
        "package",
        sa.Column("logo_mime", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("package", "logo_mime")
    op.drop_column("package", "logo")
    op.drop_column("package", "short_description")
