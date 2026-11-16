"""add_circularity_details_and_roles

Revision ID: 59a79ed71fbf
Revises: f703a183dc31
Create Date: 2026-11-15 16:01:01.328076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59a79ed71fbf'
down_revision: Union[str, Sequence[str], None] = 'f703a183dc31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    engine_name = bind.engine.name if bind else ""

    # 1. Add circularity_category and scoring_breakdown columns to analysis_records
    op.add_column('analysis_records', sa.Column('circularity_category', sa.String(length=50), nullable=True))
    op.add_column('analysis_records', sa.Column('scoring_breakdown', sa.Text(), nullable=True))

    # 2. If running on PostgreSQL, expand roleenum type
    if engine_name == "postgresql":
        op.execute("ALTER TYPE roleenum ADD VALUE IF NOT EXISTS 'SUSTAINABILITY_MANAGER';")
        op.execute("ALTER TYPE roleenum ADD VALUE IF NOT EXISTS 'MANUFACTURER';")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('analysis_records', 'scoring_breakdown')
    op.drop_column('analysis_records', 'circularity_category')
