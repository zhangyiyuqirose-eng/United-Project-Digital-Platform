-- V5__add_procurement_plan_table.sql
-- Procurement plan management table

CREATE TABLE IF NOT EXISTS pm_procurement_plan (
    plan_id           VARCHAR(64)    NOT NULL COMMENT 'Plan ID',
    project_id        VARCHAR(64)    NOT NULL COMMENT 'Project ID',
    name              VARCHAR(256)   NOT NULL COMMENT 'Plan name',
    category          VARCHAR(128)   COMMENT 'Category',
    estimated_cost    DECIMAL(18,2)  COMMENT 'Estimated cost',
    supplier_id       VARCHAR(64)    COMMENT 'Supplier ID',
    required_date     VARCHAR(32)    COMMENT 'Required delivery date',
    status            VARCHAR(32)    DEFAULT 'PLANNED' COMMENT 'Status: PLANNED/IN_PROGRESS/COMPLETED/CANCELLED',
    priority          VARCHAR(16)    COMMENT 'Priority: HIGH/MEDIUM/LOW',
    description       VARCHAR(2000)  COMMENT 'Description',
    created_by        VARCHAR(64)    COMMENT 'Created by user ID',
    created_at        VARCHAR(32)    COMMENT 'Created time',
    updated_at        VARCHAR(32)    COMMENT 'Updated time',
    PRIMARY KEY (plan_id),
    INDEX idx_project_id (project_id),
    INDEX idx_status (status),
    INDEX idx_required_date (required_date)
) COMMENT 'Procurement plan table';
