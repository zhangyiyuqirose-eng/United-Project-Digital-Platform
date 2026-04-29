"""Initial schema migration: 57 tables migrated from MySQL to PostgreSQL.

Mirrors schema.sql from the Java microservices project, adapted for PostgreSQL:
- DECIMAL -> NUMERIC
- TIMESTAMP DEFAULT CURRENT_TIMESTAMP -> TIMESTAMP DEFAULT now()
- BIGINT -> BIGINT
- TEXT -> TEXT
- INT DEFAULT -> INTEGER DEFAULT
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ── System tables ────────────────────────────────────────────────
    op.create_table(
        "pm_sys_dept",
        sa.Column("dept_id", sa.String(64), primary_key=True),
        sa.Column("dept_name", sa.String(100), nullable=False),
        sa.Column("parent_id", sa.String(64)),
        sa.Column("leader_id", sa.String(64)),
        sa.Column("sort_order", sa.Integer, server_default=sa.text("0")),
        sa.Column("status", sa.Integer, server_default=sa.text("1")),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_sys_user",
        sa.Column("user_id", sa.String(64), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False, unique=True),
        sa.Column("password", sa.String(100), nullable=False),
        sa.Column("name", sa.String(100)),
        sa.Column("dept_id", sa.String(64)),
        sa.Column("email", sa.String(100)),
        sa.Column("phone", sa.String(20)),
        sa.Column("status", sa.Integer, server_default=sa.text("1")),
        sa.Column("password_changed_at", sa.DateTime(timezone=True)),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_sys_role",
        sa.Column("role_id", sa.String(64), primary_key=True),
        sa.Column("role_name", sa.String(50), nullable=False),
        sa.Column("role_code", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(200)),
        sa.Column("status", sa.Integer, server_default=sa.text("1")),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_sys_permission",
        sa.Column("permission_id", sa.String(64), primary_key=True),
        sa.Column("permission_name", sa.String(50), nullable=False),
        sa.Column("permission_code", sa.String(100), nullable=False, unique=True),
        sa.Column("resource_type", sa.String(20)),
        sa.Column("resource_url", sa.String(200)),
        sa.Column("parent_id", sa.String(64)),
        sa.Column("status", sa.Integer, server_default=sa.text("1")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_sys_user_role",
        sa.Column("user_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("role_id", sa.String(64), primary_key=True, nullable=False),
    )

    op.create_table(
        "pm_sys_role_permission",
        sa.Column("role_id", sa.String(64), primary_key=True, nullable=False),
        sa.Column("permission_id", sa.String(64), primary_key=True, nullable=False),
    )

    op.create_table(
        "pm_sys_dict",
        sa.Column("dict_id", sa.String(64), primary_key=True),
        sa.Column("dict_type", sa.String(50), nullable=False),
        sa.Column("dict_label", sa.String(100), nullable=False),
        sa.Column("dict_value", sa.String(100), nullable=False),
        sa.Column("sort_order", sa.Integer, server_default=sa.text("0")),
        sa.Column("status", sa.Integer, server_default=sa.text("1")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_sys_config",
        sa.Column("config_id", sa.String(64), primary_key=True),
        sa.Column("config_key", sa.String(100), nullable=False, unique=True),
        sa.Column("config_value", sa.String(500)),
        sa.Column("description", sa.String(200)),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_sys_announcement",
        sa.Column("announcement_id", sa.String(64), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.Text),
        sa.Column("type", sa.String(20)),
        sa.Column("status", sa.Integer, server_default=sa.text("1")),
        sa.Column("publisher_id", sa.String(64)),
        sa.Column("publish_time", sa.TIMESTAMP),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_sys_audit_log",
        sa.Column("log_id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64)),
        sa.Column("operation", sa.String(50)),
        sa.Column("method", sa.String(100)),
        sa.Column("params", sa.Text),
        sa.Column("ip", sa.String(50)),
        sa.Column("status", sa.Integer),
        sa.Column("error_msg", sa.Text),
        sa.Column("execute_time", sa.Integer),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Meeting / Asset tables ───────────────────────────────────────
    op.create_table(
        "pm_meeting",
        sa.Column("meeting_id", sa.String(64), primary_key=True),
        sa.Column("meeting_name", sa.String(200), nullable=False),
        sa.Column("meeting_type", sa.String(20)),
        sa.Column("start_time", sa.TIMESTAMP),
        sa.Column("end_time", sa.TIMESTAMP),
        sa.Column("location", sa.String(200)),
        sa.Column("organizer_id", sa.String(64)),
        sa.Column("participants", sa.Text),
        sa.Column("status", sa.String(20)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_review_meeting",
        sa.Column("review_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64)),
        sa.Column("review_type", sa.String(20)),
        sa.Column("review_date", sa.TIMESTAMP),
        sa.Column("reviewer_id", sa.String(64)),
        sa.Column("conclusion", sa.String(200)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_review_opinion",
        sa.Column("opinion_id", sa.String(64), primary_key=True),
        sa.Column("review_id", sa.String(64)),
        sa.Column("reviewer_id", sa.String(64)),
        sa.Column("opinion_type", sa.String(20)),
        sa.Column("opinion_content", sa.Text),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_asset",
        sa.Column("asset_id", sa.String(64), primary_key=True),
        sa.Column("asset_name", sa.String(200), nullable=False),
        sa.Column("asset_type", sa.String(20)),
        sa.Column("asset_code", sa.String(50), unique=True),
        sa.Column("owner_id", sa.String(64)),
        sa.Column("location", sa.String(200)),
        sa.Column("status", sa.String(20)),
        sa.Column("purchase_date", sa.TIMESTAMP),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Project tables ───────────────────────────────────────────────
    op.create_table(
        "pm_project",
        sa.Column("project_id", sa.String(64), primary_key=True),
        sa.Column("project_name", sa.String(200), nullable=False),
        sa.Column("project_code", sa.String(50), unique=True),
        sa.Column("project_type", sa.String(20)),
        sa.Column("status", sa.String(20), server_default=sa.text("'draft'")),
        sa.Column("manager_id", sa.String(64)),
        sa.Column("manager_name", sa.String(100)),
        sa.Column("department_id", sa.String(64)),
        sa.Column("department_name", sa.String(100)),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("budget", sa.Numeric(15, 2)),
        sa.Column("customer", sa.String(200)),
        sa.Column("description", sa.Text),
        sa.Column("progress", sa.Integer, server_default=sa.text("0")),
        sa.Column("wbs_json", sa.Text),
        sa.Column("milestone_json", sa.Text),
        sa.Column("evm_pv", sa.Numeric(15, 2)),
        sa.Column("evm_ev", sa.Numeric(15, 2)),
        sa.Column("evm_ac", sa.Numeric(15, 2)),
        sa.Column("evm_cpi", sa.Numeric(10, 4)),
        sa.Column("evm_spi", sa.Numeric(10, 4)),
        sa.Column("health_score", sa.Numeric(5, 2)),
        sa.Column("init_time", sa.DateTime),
        sa.Column("start_time", sa.DateTime),
        sa.Column("end_time", sa.DateTime),
        sa.Column("actual_end_time", sa.DateTime),
        sa.Column("create_user", sa.String(64)),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_project_task",
        sa.Column("task_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("task_name", sa.String(200), nullable=False),
        sa.Column("assignee_id", sa.String(64)),
        sa.Column("assignee_name", sa.String(100)),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("priority", sa.String(20), server_default=sa.text("'medium'")),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("progress", sa.Integer, server_default=sa.text("0")),
        sa.Column("wbs_id", sa.String(64)),
        sa.Column("parent_task_id", sa.String(64)),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_wbs_node",
        sa.Column("wbs_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(50)),
        sa.Column("parent_id", sa.String(64)),
        sa.Column("level", sa.Integer),
        sa.Column("sort_order", sa.Integer),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_project_risk",
        sa.Column("risk_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("risk_code", sa.String(32)),
        sa.Column("risk_name", sa.String(200), nullable=False),
        sa.Column("title", sa.String(200)),
        sa.Column("risk_type", sa.String(20)),
        sa.Column("category", sa.String(50)),
        sa.Column("description", sa.Text),
        sa.Column("probability", sa.Integer),
        sa.Column("impact", sa.Integer),
        sa.Column("level", sa.String(20)),
        sa.Column("severity", sa.String(20)),
        sa.Column("risk_score", sa.Numeric(8, 2)),
        sa.Column("status", sa.String(20), server_default=sa.text("'open'")),
        sa.Column("mitigation", sa.Text),
        sa.Column("mitigation_plan", sa.Text),
        sa.Column("contingency_plan", sa.Text),
        sa.Column("owner_id", sa.String(64)),
        sa.Column("owner_name", sa.String(100)),
        sa.Column("owner", sa.String(64)),
        sa.Column("identified_by", sa.String(64)),
        sa.Column("identified_date", sa.DateTime),
        sa.Column("closed_date", sa.DateTime),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_project_milestone",
        sa.Column("milestone_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("milestone_name", sa.String(200), nullable=False),
        sa.Column("planned_date", sa.Date),
        sa.Column("actual_date", sa.Date),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_project_change",
        sa.Column("change_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("change_type", sa.String(20)),
        sa.Column("change_reason", sa.Text),
        sa.Column("impact_analysis", sa.Text),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("approver_id", sa.String(64)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_project_close",
        sa.Column("close_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("close_type", sa.String(20)),
        sa.Column("close_date", sa.DateTime),
        sa.Column("summary", sa.Text),
        sa.Column("lessons_learned", sa.Text),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_sprint",
        sa.Column("sprint_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("sprint_name", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("status", sa.String(20), server_default=sa.text("'planning'")),
        sa.Column("goal", sa.Text),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_pre_initiation",
        sa.Column("pre_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("feasibility_study", sa.Text),
        sa.Column("business_case", sa.Text),
        sa.Column("initial_budget", sa.Numeric(15, 2)),
        sa.Column("expected_roi", sa.Numeric(10, 2)),
        sa.Column("status", sa.String(20), server_default=sa.text("'draft'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_progress_alert",
        sa.Column("alert_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("task_id", sa.String(64)),
        sa.Column("alert_type", sa.String(20)),
        sa.Column("alert_level", sa.String(20)),
        sa.Column("message", sa.Text),
        sa.Column("is_handled", sa.Integer, server_default=sa.text("0")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_code_repo",
        sa.Column("repo_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("repo_name", sa.String(200), nullable=False),
        sa.Column("repo_url", sa.String(500)),
        sa.Column("branch", sa.String(100)),
        sa.Column("last_commit", sa.String(100)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_build_record",
        sa.Column("build_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("build_number", sa.String(50)),
        sa.Column("build_status", sa.String(20)),
        sa.Column("build_time", sa.DateTime),
        sa.Column("duration", sa.Integer),
        sa.Column("log_url", sa.String(500)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_project_dependency",
        sa.Column("dep_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("depends_on_project_id", sa.String(64), nullable=False),
        sa.Column("dependency_type", sa.String(20)),
        sa.Column("description", sa.Text),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Resource tables ──────────────────────────────────────────────
    op.create_table(
        "pm_resource_pool",
        sa.Column("pool_id", sa.String(64), primary_key=True),
        sa.Column("pool_name", sa.String(100), nullable=False),
        sa.Column("manager_id", sa.String(64)),
        sa.Column("description", sa.String(500)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_leave_request",
        sa.Column("leave_id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("leave_type", sa.String(20)),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("days", sa.Integer),
        sa.Column("reason", sa.Text),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("approver_id", sa.String(64)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_performance_eval",
        sa.Column("eval_id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("project_id", sa.String(64)),
        sa.Column("period", sa.String(20)),
        sa.Column("score", sa.Numeric(5, 2)),
        sa.Column("evaluator_id", sa.String(64)),
        sa.Column("comments", sa.Text),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_personnel_replacement",
        sa.Column("replace_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("original_user_id", sa.String(64)),
        sa.Column("new_user_id", sa.String(64)),
        sa.Column("reason", sa.Text),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_resource_outsourcing",
        sa.Column("outsource_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("vendor_name", sa.String(200)),
        sa.Column("resource_count", sa.Integer),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("contract_id", sa.String(64)),
        sa.Column("status", sa.String(20), server_default=sa.text("'active'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Timesheet tables ─────────────────────────────────────────────
    op.create_table(
        "pm_timesheet",
        sa.Column("timesheet_id", sa.String(64), primary_key=True),
        sa.Column("staff_id", sa.String(64), nullable=False),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("work_date", sa.Date, nullable=False),
        sa.Column("hours", sa.Numeric(5, 2), nullable=False),
        sa.Column("check_status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("attendance_check_result", sa.String(200)),
        sa.Column("remark", sa.Text),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_timesheet_attendance",
        sa.Column("attendance_id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("check_in_time", sa.DateTime),
        sa.Column("check_out_time", sa.DateTime),
        sa.Column("status", sa.String(20)),
        sa.Column("project_id", sa.String(64)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Cost tables ──────────────────────────────────────────────────
    op.create_table(
        "pm_budget",
        sa.Column("budget_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("budget_year", sa.Integer),
        sa.Column("total_budget", sa.Numeric(15, 2)),
        sa.Column("labor_budget", sa.Numeric(15, 2)),
        sa.Column("outsource_budget", sa.Numeric(15, 2)),
        sa.Column("procurement_budget", sa.Numeric(15, 2)),
        sa.Column("other_budget", sa.Numeric(15, 2)),
        sa.Column("approved_by", sa.String(64)),
        sa.Column("approved_date", sa.DateTime),
        sa.Column("status", sa.String(20), server_default=sa.text("'DRAFT'")),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_cost",
        sa.Column("cost_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("cost_type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("calculate_time", sa.DateTime),
        sa.Column("evm_pv", sa.Numeric(15, 2)),
        sa.Column("evm_ev", sa.Numeric(15, 2)),
        sa.Column("evm_ac", sa.Numeric(15, 2)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_cost_alert",
        sa.Column("alert_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("budget_id", sa.String(64)),
        sa.Column("alert_type", sa.String(20)),
        sa.Column("threshold", sa.Numeric(15, 2)),
        sa.Column("current_value", sa.Numeric(15, 2)),
        sa.Column("message", sa.Text),
        sa.Column("is_handled", sa.Integer, server_default=sa.text("0")),
        sa.Column("severity", sa.String(20)),
        sa.Column("status", sa.String(20), server_default=sa.text("'ACTIVE'")),
        sa.Column("created_by", sa.String(64)),
        sa.Column("ack_time", sa.DateTime),
        sa.Column("resolve_time", sa.DateTime),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_cost_outsource",
        sa.Column("outsource_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("vendor_name", sa.String(200)),
        sa.Column("contract_amount", sa.Numeric(15, 2)),
        sa.Column("paid_amount", sa.Numeric(15, 2), server_default=sa.text("0")),
        sa.Column("status", sa.String(20), server_default=sa.text("'active'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_expense_reimbursement",
        sa.Column("expense_id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("project_id", sa.String(64)),
        sa.Column("expense_type", sa.String(20)),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("apply_date", sa.Date),
        sa.Column("description", sa.Text),
        sa.Column("attachments", sa.Text),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("approver_id", sa.String(64)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Business tables ──────────────────────────────────────────────
    op.create_table(
        "pm_contract",
        sa.Column("contract_id", sa.String(64), primary_key=True),
        sa.Column("contract_code", sa.String(50), unique=True),
        sa.Column("contract_name", sa.String(200), nullable=False),
        sa.Column("contract_type", sa.String(20)),
        sa.Column("party_a", sa.String(200)),
        sa.Column("party_b", sa.String(200)),
        sa.Column("total_amount", sa.Numeric(15, 2)),
        sa.Column("currency", sa.String(10)),
        sa.Column("sign_date", sa.String(20)),
        sa.Column("start_date", sa.String(20)),
        sa.Column("end_date", sa.String(20)),
        sa.Column("project_id", sa.String(64)),
        sa.Column("status", sa.String(20), server_default=sa.text("'draft'")),
        sa.Column("created_by", sa.String(64)),
        sa.Column("create_time", sa.String(30)),
        sa.Column("update_time", sa.String(30)),
        sa.Column("reminder_days", sa.Integer),
    )

    op.create_table(
        "pm_contract_payment",
        sa.Column("payment_id", sa.String(64), primary_key=True),
        sa.Column("contract_id", sa.String(64), nullable=False),
        sa.Column("payment_type", sa.String(20)),
        sa.Column("planned_amount", sa.Numeric(15, 2)),
        sa.Column("actual_amount", sa.Numeric(15, 2)),
        sa.Column("planned_date", sa.Date),
        sa.Column("actual_date", sa.Date),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_customer",
        sa.Column("customer_id", sa.String(64), primary_key=True),
        sa.Column("customer_name", sa.String(200), nullable=False),
        sa.Column("customer_type", sa.String(20)),
        sa.Column("contact_person", sa.String(100)),
        sa.Column("phone", sa.String(20)),
        sa.Column("email", sa.String(100)),
        sa.Column("address", sa.String(500)),
        sa.Column("industry", sa.String(100)),
        sa.Column("status", sa.String(20), server_default=sa.text("'active'")),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "pm_supplier",
        sa.Column("supplier_id", sa.String(64), primary_key=True),
        sa.Column("supplier_name", sa.String(200), nullable=False),
        sa.Column("supplier_type", sa.String(20)),
        sa.Column("contact_person", sa.String(100)),
        sa.Column("phone", sa.String(20)),
        sa.Column("email", sa.String(100)),
        sa.Column("address", sa.String(500)),
        sa.Column("status", sa.String(20), server_default=sa.text("'active'")),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "pm_business_opportunity",
        sa.Column("opportunity_id", sa.String(64), primary_key=True),
        sa.Column("opportunity_name", sa.String(200), nullable=False),
        sa.Column("customer_id", sa.String(64)),
        sa.Column("expected_amount", sa.Numeric(15, 2)),
        sa.Column("probability", sa.Integer),
        sa.Column("stage", sa.String(20)),
        sa.Column("owner_id", sa.String(64)),
        sa.Column("expected_close_date", sa.Date),
        sa.Column("status", sa.String(20), server_default=sa.text("'open'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_quotation",
        sa.Column("quotation_id", sa.String(64), primary_key=True),
        sa.Column("opportunity_id", sa.String(64)),
        sa.Column("customer_id", sa.String(64)),
        sa.Column("quotation_no", sa.String(50)),
        sa.Column("amount", sa.Numeric(15, 2)),
        sa.Column("valid_until", sa.Date),
        sa.Column("status", sa.String(20), server_default=sa.text("'draft'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_procurement_plan",
        sa.Column("plan_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("plan_name", sa.String(200), nullable=False),
        sa.Column("procurement_type", sa.String(20)),
        sa.Column("budget", sa.Numeric(15, 2)),
        sa.Column("planned_date", sa.Date),
        sa.Column("status", sa.String(20), server_default=sa.text("'draft'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Knowledge tables ─────────────────────────────────────────────
    op.create_table(
        "pm_knowledge_doc",
        sa.Column("doc_id", sa.String(64), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("doc_type", sa.String(20)),
        sa.Column("template_type", sa.String(20)),
        sa.Column("category", sa.String(100)),
        sa.Column("content", sa.Text),
        sa.Column("author_id", sa.String(64)),
        sa.Column("created_by", sa.String(64)),
        sa.Column("version", sa.String(20)),
        sa.Column("version_num", sa.Integer),
        sa.Column("file_path", sa.String(500)),
        sa.Column("status", sa.String(20), server_default=sa.text("'draft'")),
        sa.Column("publish_time", sa.DateTime),
        sa.Column("create_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("update_time", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "pm_knowledge_template",
        sa.Column("template_id", sa.String(64), primary_key=True),
        sa.Column("template_name", sa.String(200), nullable=False),
        sa.Column("template_type", sa.String(20)),
        sa.Column("content", sa.Text),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.String(20), server_default=sa.text("'active'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_knowledge_review",
        sa.Column("review_id", sa.String(64), primary_key=True),
        sa.Column("doc_id", sa.String(64), nullable=False),
        sa.Column("reviewer_id", sa.String(64)),
        sa.Column("review_status", sa.String(20)),
        sa.Column("comments", sa.Text),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_compliance_checklist",
        sa.Column("checklist_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("checklist_name", sa.String(200), nullable=False),
        sa.Column("checklist_type", sa.String(20)),
        sa.Column("items", sa.Text),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Quality tables ───────────────────────────────────────────────
    op.create_table(
        "pm_quality_defect",
        sa.Column("defect_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("defect_name", sa.String(200), nullable=False),
        sa.Column("defect_type", sa.String(20)),
        sa.Column("severity", sa.String(20)),
        sa.Column("status", sa.String(20), server_default=sa.text("'open'")),
        sa.Column("found_by", sa.String(64)),
        sa.Column("assigned_to", sa.String(64)),
        sa.Column("found_date", sa.Date),
        sa.Column("fixed_date", sa.Date),
        sa.Column("description", sa.Text),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_quality_metric",
        sa.Column("metric_id", sa.String(64), primary_key=True),
        sa.Column("project_id", sa.String(64), nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("metric_value", sa.Numeric(10, 2)),
        sa.Column("target_value", sa.Numeric(10, 2)),
        sa.Column("measurement_date", sa.Date),
        sa.Column("unit", sa.String(20)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── File table ───────────────────────────────────────────────────
    op.create_table(
        "pm_file_info",
        sa.Column("file_id", sa.String(64), primary_key=True),
        sa.Column("file_name", sa.String(200), nullable=False),
        sa.Column("file_path", sa.String(500)),
        sa.Column("file_type", sa.String(50)),
        sa.Column("file_size", sa.BigInteger),
        sa.Column("project_id", sa.String(64)),
        sa.Column("uploader_id", sa.String(64)),
        sa.Column("download_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Notify tables ────────────────────────────────────────────────
    op.create_table(
        "pm_notify_message",
        sa.Column("message_id", sa.String(64), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.Text),
        sa.Column("type", sa.String(20)),
        sa.Column("sender_id", sa.String(64)),
        sa.Column("receiver_id", sa.String(64)),
        sa.Column("status", sa.String(20), server_default=sa.text("'unread'")),
        sa.Column("send_time", sa.DateTime, server_default=sa.func.now()),
        sa.Column("read_time", sa.DateTime),
    )

    op.create_table(
        "pm_notify_template",
        sa.Column("template_id", sa.String(64), primary_key=True),
        sa.Column("template_name", sa.String(100), nullable=False),
        sa.Column("template_code", sa.String(50), unique=True),
        sa.Column("template_content", sa.Text),
        sa.Column("type", sa.String(20)),
        sa.Column("status", sa.String(20), server_default=sa.text("'active'")),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_table(
        "pm_notify_preference",
        sa.Column("pref_id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False),
        sa.Column("notify_type", sa.String(20)),
        sa.Column("enabled", sa.Integer, server_default=sa.text("1")),
        sa.Column("channel", sa.String(20)),
        sa.Column("create_time", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    # ── Audit table ──────────────────────────────────────────────────
    op.create_table(
        "pm_audit_log_entry",
        sa.Column("entry_id", sa.String(64), primary_key=True),
        sa.Column("audit_id", sa.String(64)),
        sa.Column("user_id", sa.String(64)),
        sa.Column("action", sa.String(50)),
        sa.Column("resource_type", sa.String(50)),
        sa.Column("resource_id", sa.String(64)),
        sa.Column("details", sa.Text),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now()),
    )

    # ── Auth table ───────────────────────────────────────────────────
    op.create_table(
        "pm_login_attempt",
        sa.Column("attempt_id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64)),
        sa.Column("username", sa.String(50)),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("success", sa.Integer, server_default=sa.text("0")),
        sa.Column("failure_reason", sa.String(200)),
        sa.Column("attempt_time", sa.DateTime, server_default=sa.func.now()),
    )

    # ── Workflow table ───────────────────────────────────────────────
    op.create_table(
        "pm_process_definition",
        sa.Column("def_id", sa.String(64), primary_key=True),
        sa.Column("process_key", sa.String(100), nullable=False, unique=True),
        sa.Column("process_name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50)),
        sa.Column("deployment_id", sa.String(100)),
        sa.Column("version", sa.Integer, server_default=sa.text("1")),
        sa.Column("status", sa.String(20), server_default=sa.text("'active'")),
        sa.Column("create_time", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    # Drop tables in reverse dependency order
    tables = [
        "pm_process_definition", "pm_login_attempt", "pm_audit_log_entry",
        "pm_notify_preference", "pm_notify_template", "pm_notify_message",
        "pm_file_info", "pm_quality_metric", "pm_quality_defect",
        "pm_compliance_checklist", "pm_knowledge_review", "pm_knowledge_template",
        "pm_knowledge_doc", "pm_procurement_plan", "pm_quotation",
        "pm_business_opportunity", "pm_supplier", "pm_customer",
        "pm_contract_payment", "pm_contract", "pm_expense_reimbursement",
        "pm_cost_outsource", "pm_cost_alert", "pm_cost", "pm_budget",
        "pm_timesheet_attendance", "pm_timesheet", "pm_resource_outsourcing",
        "pm_personnel_replacement", "pm_performance_eval", "pm_leave_request",
        "pm_resource_pool", "pm_project_dependency", "pm_build_record",
        "pm_code_repo", "pm_progress_alert", "pm_pre_initiation", "pm_sprint",
        "pm_project_close", "pm_project_change", "pm_project_milestone",
        "pm_project_risk", "pm_wbs_node", "pm_project_task", "pm_project",
        "pm_asset", "pm_review_opinion", "pm_review_meeting", "pm_meeting",
        "pm_sys_audit_log", "pm_sys_announcement", "pm_sys_config",
        "pm_sys_dict", "pm_sys_role_permission", "pm_sys_user_role",
        "pm_sys_permission", "pm_sys_role", "pm_sys_user", "pm_sys_dept",
    ]
    for table in tables:
        op.drop_table(table)
