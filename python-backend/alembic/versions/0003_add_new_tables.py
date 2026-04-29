"""add report, settlement, document version, policy tables

Revision ID: 0003_add_new_tables
Revises: 0002_add_data_permission
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_add_new_tables"
down_revision = "0002_add_data_permission"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pm_report_history",
        sa.Column("report_id", sa.String(64), primary_key=True),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(64)),
        sa.Column("file_name", sa.String(200), nullable=False),
        sa.Column("file_size", sa.Integer),
        sa.Column("status", sa.String(20), nullable=False, server_default="generated"),
        sa.Column("created_by", sa.String(64)),
        sa.Column("error_message", sa.Text),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "pm_cost_settlement",
        sa.Column("settlement_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("settlement_amount", sa.Numeric(15, 2)),
        sa.Column("settlement_date", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_by", sa.String(64)),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "pm_document_version",
        sa.Column("version_id", sa.String(64), primary_key=True),
        sa.Column("doc_id", sa.String(64), nullable=False),
        sa.Column("version", sa.String(20)),
        sa.Column("version_num", sa.Integer),
        sa.Column("content", sa.Text),
        sa.Column("created_by", sa.String(64)),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "pm_policy",
        sa.Column("policy_id", sa.String(64), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("policy_type", sa.String(20)),
        sa.Column("content", sa.Text),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("pm_policy")
    op.drop_table("pm_document_version")
    op.drop_table("pm_cost_settlement")
    op.drop_table("pm_report_history")
