"""Add Go-Live import fields to Booking model - PostgreSQL compatible

Revision ID: add_go_live_import_fields_manual
Revises: e52c863e9aca
Create Date: 2025-10-08 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_go_live_import_fields_manual"
down_revision: Union[str, Sequence[str], None] = "e52c863e9aca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Go-Live import fields to Booking table - PostgreSQL compatible."""
    # Add new columns to booking table
    op.add_column("booking", sa.Column("source", sa.String(length=50), nullable=True))
    op.add_column("booking", sa.Column("channel", sa.String(length=100), nullable=True))
    op.add_column(
        "booking", sa.Column("external_ref", sa.String(length=255), nullable=True)
    )
    op.add_column("booking", sa.Column("imported_at", sa.DateTime(), nullable=True))
    op.add_column(
        "booking", sa.Column("ingestion_id", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "booking", sa.Column("row_hash", sa.String(length=255), nullable=True)
    )

    # Create indexes for performance (PostgreSQL compatible)
    op.create_index("idx_booking_source", "booking", ["source"])
    op.create_index("idx_booking_channel", "booking", ["channel"])
    op.create_index("idx_booking_external_ref", "booking", ["external_ref"])
    op.create_index("idx_booking_imported_at", "booking", ["imported_at"])
    op.create_index("idx_booking_ingestion_id", "booking", ["ingestion_id"])
    op.create_index("idx_booking_row_hash", "booking", ["row_hash"])

    # Composite indexes for common queries
    op.create_index("idx_booking_source_channel", "booking", ["source", "channel"])


def downgrade() -> None:
    """Remove Go-Live import fields from Booking table."""
    # Drop indexes first
    op.drop_index("idx_booking_source_channel", table_name="booking")
    op.drop_index("idx_booking_row_hash", table_name="booking")
    op.drop_index("idx_booking_ingestion_id", table_name="booking")
    op.drop_index("idx_booking_imported_at", table_name="booking")
    op.drop_index("idx_booking_external_ref", table_name="booking")
    op.drop_index("idx_booking_channel", table_name="booking")
    op.drop_index("idx_booking_source", table_name="booking")

    # Drop columns
    op.drop_column("booking", "row_hash")
    op.drop_column("booking", "ingestion_id")
    op.drop_column("booking", "imported_at")
    op.drop_column("booking", "external_ref")
    op.drop_column("booking", "channel")
    op.drop_column("booking", "source")
