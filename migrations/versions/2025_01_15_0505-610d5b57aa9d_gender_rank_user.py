"""Gender Rank user

Revision ID: 610d5b57aa9d
Revises: c6d410aaf79a
Create Date: 2025-01-15 05:05:02.055377

"""
from typing import Sequence, Union

# Define ENUM types
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '610d5b57aa9d'
down_revision: Union[str, None] = 'c6d410aaf79a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ENUM 타입 정의
gender_enum = ENUM('MALE', 'FEMALE', name='gender', create_type=False)
rank_enum = ENUM('BRONZE', 'SILVER', 'GOLD', name='rank', create_type=False)

def upgrade():
    # ENUM 타입 생성
    gender_enum.create(op.get_bind(), checkfirst=True)
    rank_enum.create(op.get_bind(), checkfirst=True)

    # gender 열을 ENUM 타입으로 변경
    op.execute("ALTER TABLE \"User\" ALTER COLUMN gender TYPE gender USING gender::gender")

    # rank 열을 ENUM 타입으로 변경
    op.execute("ALTER TABLE \"User\" ALTER COLUMN rank TYPE rank USING rank::rank")


def downgrade():
    # gender 열을 VARCHAR로 다시 변경
    op.execute("ALTER TABLE \"User\" ALTER COLUMN gender TYPE VARCHAR(255)")

    # rank 열을 VARCHAR로 다시 변경
    op.execute("ALTER TABLE \"User\" ALTER COLUMN rank TYPE VARCHAR(255)")

    # ENUM 타입 제거
    gender_enum.drop(op.get_bind(), checkfirst=True)
    rank_enum.drop(op.get_bind(), checkfirst=True)
