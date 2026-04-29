"""Add data permission: data_scope to roles, data permission config tables.

Migration 0002:
- Adds data_scope column to pm_sys_role (default 'all' for backward compatibility)
- Creates sys_data_permission table for configurable data permission rules
- Creates sys_role_data_permission junction table
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # ── Add data_scope to roles ──────────────────────────────────────
    op.add_column(
        "pm_sys_role",
        sa.Column("data_scope", sa.String(20), server_default="all", nullable=False),
    )

    # Set existing roles to 'all' scope (backward compatible)
    op.execute("UPDATE pm_sys_role SET data_scope = 'all'")

    # ── Data permission configuration table ──────────────────────────
    op.create_table(
        "sys_data_permission",
        sa.Column("permission_id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("table_name", sa.String(100), nullable=False),
        sa.Column("owner_field", sa.String(50), server_default="owner_id"),
        sa.Column("dept_field", sa.String(50), server_default="dept_id"),
        sa.Column("data_scope", sa.String(20), server_default="all"),
        sa.Column("custom_filter", sa.Text),
        sa.Column("status", sa.Integer, server_default=sa.text("1")),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Role-data-permission junction table ──────────────────────────
    op.create_table(
        "sys_role_data_permission",
        sa.Column("role_id", sa.String(64), primary_key=True),
        sa.Column("permission_id", sa.String(64), primary_key=True),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── Indexes ──────────────────────────────────────────────────────
    op.create_index("ix_data_permission_code", "sys_data_permission", ["code"])
    op.create_index("ix_data_permission_resource", "sys_data_permission", ["resource_type"])


def downgrade():
    op.drop_table("sys_role_data_permission")
    op.drop_table("sys_data_permission")
    op.drop_column("pm_sys_role", "data_scope")
