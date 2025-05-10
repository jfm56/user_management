"""merge heads

Revision ID: 85a862c1ee7c
Revises: 25d814bc83ed, 29c845461887
Create Date: 2025-05-10 04:00:18.276941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85a862c1ee7c'
down_revision: Union[str, None] = ('25d814bc83ed', '29c845461887')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
