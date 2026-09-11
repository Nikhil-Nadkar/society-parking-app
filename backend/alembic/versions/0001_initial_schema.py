"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-11

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("room_no", sa.String(20), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("RESIDENT", "ADMIN", name="userrole"), nullable=False, server_default="RESIDENT"),
        sa.Column("parking_slot_id", sa.Integer(), nullable=True, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "parking_slots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("slot_number", sa.String(20), nullable=False, unique=True),
        sa.Column("type", sa.Enum("RESIDENT", "GUEST", "DELIVERY", name="slottype"), nullable=False, server_default="RESIDENT"),
        sa.Column("status", sa.Enum("UNUSED", "ASSIGNED", name="slotstatus"), nullable=False, server_default="UNUSED"),
        sa.Column("assigned_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_parking_slots_slot_number", "parking_slots", ["slot_number"])

    # users.parking_slot_id -> parking_slots.id (deferred: circular reference with parking_slots)
    op.create_foreign_key(
        "fk_users_parking_slot_id",
        "users",
        "parking_slots",
        ["parking_slot_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parking_slot_id", sa.Integer(), sa.ForeignKey("parking_slots.id", ondelete="SET NULL"), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", "OVERDUE", "NOT_DUE", name="paymentstatus"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rejection_reason", sa.String(500), nullable=True),
        sa.UniqueConstraint("user_id", "month", "year", "status", name="uq_user_month_year_status"),
    )
    op.create_index("ix_payment_user_period", "payments", ["user_id", "year", "month"])

    op.create_table(
        "payment_screenshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("payments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("payment_screenshots")
    op.drop_table("payments")
    op.drop_constraint("fk_users_parking_slot_id", "users", type_="foreignkey")
    op.drop_table("parking_slots")
    op.drop_table("users")
