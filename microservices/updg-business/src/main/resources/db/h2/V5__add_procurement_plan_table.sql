-- V5__add_procurement_plan_table.sql
-- Procurement plan management table (H2)

CREATE TABLE IF NOT EXISTS pm_procurement_plan (
    plan_id           VARCHAR(64)    NOT NULL,
    project_id        VARCHAR(64)    NOT NULL,
    name              VARCHAR(256)   NOT NULL,
    category          VARCHAR(128),
    estimated_cost    DECIMAL(18,2),
    supplier_id       VARCHAR(64),
    required_date     VARCHAR(32),
    status            VARCHAR(32)    DEFAULT 'PLANNED',
    priority          VARCHAR(16),
    description       VARCHAR(2000),
    created_by        VARCHAR(64),
    created_at        VARCHAR(32),
    updated_at        VARCHAR(32),
    PRIMARY KEY (plan_id)
);

CREATE INDEX IF NOT EXISTS idx_plan_proj_id ON pm_procurement_plan(project_id);
CREATE INDEX IF NOT EXISTS idx_plan_status ON pm_procurement_plan(status);
CREATE INDEX IF NOT EXISTS idx_plan_req_date ON pm_procurement_plan(required_date);
