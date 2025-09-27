"""Add category_id to ExtraCharge

Revision ID: ff2cc8a4dc60
Revises: 
Create Date: 2025-09-07 11:01:13.465017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'ff2cc8a4dc60'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Kiểm tra sự tồn tại của bảng trước khi tạo
    conn = op.get_bind()
    inspector = inspect(conn)

    if "extra_charges_temp" not in inspector.get_table_names():
        op.create_table(
            "extra_charges_temp",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("property_id", sa.Integer, nullable=False),
            sa.Column("charge_name", sa.String, nullable=False),
            sa.Column("charge_amount", sa.Integer, nullable=False),
            sa.Column("charge_month", sa.String, nullable=False),
            sa.Column("charge_note", sa.String, nullable=True),
            sa.Column("created_at", sa.String, nullable=True),
            sa.Column("category_id", sa.Integer, nullable=True),
        )

    # Sao chép dữ liệu từ bảng cũ sang bảng tạm
    if "extra_charges" in inspector.get_table_names():
        op.execute(
            """
            INSERT INTO extra_charges_temp (id, property_id, charge_name, charge_amount, charge_month, charge_note, created_at)
            SELECT id, property_id, charge_name, charge_amount, charge_month, charge_note, created_at
            FROM extra_charges
            """
        )

        # Xóa bảng cũ
        op.drop_table("extra_charges")

    # Đổi tên bảng tạm thành bảng chính
    op.rename_table("extra_charges_temp", "extra_charges")


def downgrade() -> None:
    """Downgrade schema."""
    # Tạo lại bảng cũ không có cột category_id
    conn = op.get_bind()
    inspector = inspect(conn)

    if "extra_charges" in inspector.get_table_names():
        op.create_table(
            "extra_charges_temp",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("property_id", sa.Integer, nullable=False),
            sa.Column("charge_name", sa.String, nullable=False),
            sa.Column("charge_amount", sa.Integer, nullable=False),
            sa.Column("charge_month", sa.String, nullable=False),
            sa.Column("charge_note", sa.String, nullable=True),
            sa.Column("created_at", sa.String, nullable=True),
        )

        op.execute(
            """
            INSERT INTO extra_charges_temp (id, property_id, charge_name, charge_amount, charge_month, charge_note, created_at)
            SELECT id, property_id, charge_name, charge_amount, charge_month, charge_note, created_at
            FROM extra_charges
            """
        )

        op.drop_table("extra_charges")
        op.rename_table("extra_charges_temp", "extra_charges")
